"""
Streaming System pour Vectort.io
Affiche la progression en temps réel comme Emergent
"""

import asyncio
import logging
from typing import AsyncGenerator, Dict, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class StreamingMessage:
    """Message de streaming avec type et contenu"""
    
    def __init__(
        self,
        message_type: str,
        content: str,
        agent: str = None,
        file_path: str = None,
        progress: int = 0,
        metadata: Dict = None
    ):
        self.message_type = message_type  # info, success, error, progress, file_created
        self.content = content
        self.agent = agent
        self.file_path = file_path
        self.progress = progress
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        """Convertit en dict pour SSE"""
        return {
            "type": self.message_type,
            "content": self.content,
            "agent": self.agent,
            "file_path": self.file_path,
            "progress": self.progress,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def to_sse_format(self) -> str:
        """Formate pour Server-Sent Events"""
        data = json.dumps(self.to_dict())
        return f"data: {data}\n\n"


class StreamingQueue:
    """Queue pour gérer les messages de streaming"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.active = True
    
    async def send(self, message: StreamingMessage):
        """Envoie un message dans la queue"""
        if self.active:
            await self.queue.put(message)
    
    async def receive(self) -> StreamingMessage:
        """Reçoit un message de la queue"""
        return await self.queue.get()
    
    def close(self):
        """Ferme la queue"""
        self.active = False


class GenerationStreamer:
    """
    Streamer pour la génération multi-agents
    Affiche la progression en temps réel
    """
    
    def __init__(self):
        self.queues: Dict[str, StreamingQueue] = {}
        self.generation_states: Dict[str, Dict] = {}
    
    def create_stream(self, project_id: str) -> StreamingQueue:
        """Crée un nouveau stream pour un projet"""
        queue = StreamingQueue()
        self.queues[project_id] = queue
        self.generation_states[project_id] = {
            "phase": "init",
            "progress": 0,
            "agents_completed": [],
            "files_created": []
        }
        
        logger.info(f"📡 Stream créé pour projet: {project_id}")
        return queue
    
    def get_stream(self, project_id: str) -> StreamingQueue:
        """Récupère un stream existant"""
        return self.queues.get(project_id)
    
    async def send_message(
        self,
        project_id: str,
        message_type: str,
        content: str,
        agent: str = None,
        file_path: str = None,
        progress: int = None
    ):
        """Envoie un message dans le stream"""
        queue = self.queues.get(project_id)
        if not queue:
            return
        
        # Mettre à jour l'état
        state = self.generation_states.get(project_id, {})
        if progress is not None:
            state["progress"] = progress
        if agent and message_type == "success":
            if agent not in state.get("agents_completed", []):
                state["agents_completed"].append(agent)
        if file_path:
            if file_path not in state.get("files_created", []):
                state["files_created"].append(file_path)
        
        message = StreamingMessage(
            message_type=message_type,
            content=content,
            agent=agent,
            file_path=file_path,
            progress=progress or state.get("progress", 0),
            metadata={"state": state}
        )
        
        await queue.send(message)
        logger.debug(f"📤 Message envoyé: {content[:50]}")
    
    async def stream_phase(self, project_id: str, phase_name: str, phase_number: int):
        """Annonce une nouvelle phase"""
        await self.send_message(
            project_id,
            "phase",
            f"🔄 Phase {phase_number}: {phase_name}",
            progress=(phase_number - 1) * 20  # 5 phases = 20% chacune
        )
    
    async def stream_agent_start(self, project_id: str, agent_name: str):
        """Agent démarre"""
        await self.send_message(
            project_id,
            "info",
            f"🤖 Agent {agent_name} démarré...",
            agent=agent_name
        )
    
    async def stream_agent_complete(self, project_id: str, agent_name: str, files_count: int):
        """Agent terminé"""
        await self.send_message(
            project_id,
            "success",
            f"✅ Agent {agent_name} terminé - {files_count} fichiers générés",
            agent=agent_name
        )
    
    async def stream_file_created(self, project_id: str, file_path: str, size: int):
        """Fichier créé"""
        await self.send_message(
            project_id,
            "file_created",
            f"📄 Fichier créé: {file_path} ({size} bytes)",
            file_path=file_path
        )
    
    async def stream_error(self, project_id: str, error_message: str, agent: str = None):
        """Erreur"""
        await self.send_message(
            project_id,
            "error",
            f"❌ Erreur: {error_message}",
            agent=agent
        )
    
    async def stream_completion(self, project_id: str, total_files: int, total_time: float, score: float):
        """Génération terminée"""
        await self.send_message(
            project_id,
            "complete",
            f"🎉 Génération terminée - {total_files} fichiers en {total_time:.1f}s - Score: {score:.1f}/100",
            progress=100
        )
    
    async def generate_sse_stream(self, project_id: str) -> AsyncGenerator[str, None]:
        """
        Génère un stream SSE (Server-Sent Events)
        
        Utilisé par l'endpoint FastAPI pour envoyer les messages en temps réel
        """
        queue = self.queues.get(project_id)
        if not queue:
            logger.error(f"❌ Pas de queue pour projet: {project_id}")
            return
        
        logger.info(f"📡 Début streaming pour projet: {project_id}")
        
        try:
            while queue.active:
                try:
                    # Attendre message avec timeout
                    message = await asyncio.wait_for(queue.receive(), timeout=1.0)
                    
                    # Convertir en format SSE
                    sse_data = message.to_sse_format()
                    yield sse_data
                    
                    # Si message de completion, terminer
                    if message.message_type == "complete":
                        logger.info(f"✅ Stream terminé pour projet: {project_id}")
                        break
                    
                except asyncio.TimeoutError:
                    # Envoyer keepalive toutes les 1s
                    yield ": keepalive\n\n"
                    
        except Exception as e:
            logger.error(f"❌ Erreur streaming: {e}")
            error_msg = StreamingMessage(
                "error",
                f"Erreur streaming: {str(e)}"
            )
            yield error_msg.to_sse_format()
        
        finally:
            # Nettoyer
            self.close_stream(project_id)
    
    def close_stream(self, project_id: str):
        """Ferme et nettoie un stream"""
        if project_id in self.queues:
            self.queues[project_id].close()
            del self.queues[project_id]
        
        if project_id in self.generation_states:
            del self.generation_states[project_id]
        
        logger.info(f"🔒 Stream fermé pour projet: {project_id}")
    
    def get_generation_state(self, project_id: str) -> Dict:
        """Récupère l'état actuel d'une génération"""
        return self.generation_states.get(project_id, {})


# Instance globale
streaming_manager = GenerationStreamer()


# Export
__all__ = ['StreamingMessage', 'GenerationStreamer', 'streaming_manager']
