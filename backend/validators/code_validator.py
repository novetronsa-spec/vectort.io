"""
VECTORT.IO - CODE VALIDATOR
Système de validation et tests automatiques du code généré
"""

import re
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Résultat de validation d'un fichier"""
    file_path: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    score: float  # 0-100


class CodeValidator:
    """Valide le code généré"""
    
    def __init__(self):
        self.validators = {
            '.jsx': self._validate_jsx,
            '.js': self._validate_javascript,
            '.tsx': self._validate_tsx,
            '.ts': self._validate_typescript,
            '.py': self._validate_python,
            '.json': self._validate_json,
            '.html': self._validate_html,
            '.css': self._validate_css,
        }
    
    def validate_project(self, all_files: Dict[str, str]) -> Dict[str, ValidationResult]:
        """Valide tous les fichiers d'un projet"""
        
        results = {}
        
        for file_path, content in all_files.items():
            # Déterminer le type de fichier
            extension = self._get_extension(file_path)
            
            validator = self.validators.get(extension, self._validate_generic)
            result = validator(file_path, content)
            
            results[file_path] = result
        
        return results
    
    def get_project_score(self, results: Dict[str, ValidationResult]) -> float:
        """Calcule le score global du projet"""
        
        if not results:
            return 0.0
        
        total_score = sum(r.score for r in results.values())
        return total_score / len(results)
    
    def _get_extension(self, file_path: str) -> str:
        """Extrait l'extension du fichier"""
        if '.' not in file_path:
            return ''
        return '.' + file_path.split('.')[-1]
    
    def _validate_jsx(self, file_path: str, content: str) -> ValidationResult:
        """Valide un fichier JSX/React"""
        
        errors = []
        warnings = []
        
        # Vérifications de base
        if not content.strip():
            errors.append("Fichier vide")
            return ValidationResult(file_path, False, errors, warnings, 0.0)
        
        # Import React
        if 'import React' not in content and 'import {' not in content:
            warnings.append("Imports React manquants ou inhabituels")
        
        # Export default
        if 'export default' not in content:
            errors.append("Pas d'export default")
        
        # Syntaxe JSX de base
        if '<' in content and '>' in content:
            # Vérifier les balises fermées
            open_tags = len(re.findall(r'<\w+[^/>]*>', content))
            self_closing = len(re.findall(r'<\w+[^>]*/>', content))
            close_tags = len(re.findall(r'</\w+>', content))
            
            if open_tags - self_closing != close_tags:
                warnings.append("Possible déséquilibre de balises JSX")
        
        # PropTypes ou TypeScript
        if 'PropTypes' not in content and '.tsx' not in file_path:
            warnings.append("PropTypes non définis (considérer TypeScript)")
        
        # Hooks
        if any(hook in content for hook in ['useState', 'useEffect', 'useContext']):
            # Vérifier que les hooks sont utilisés correctement
            if 'function' in content.lower() or 'const' in content:
                pass  # OK
            else:
                warnings.append("Hooks détectés mais structure inhabituelle")
        
        # Score
        score = 100.0
        score -= len(errors) * 20
        score -= len(warnings) * 5
        score = max(0, min(100, score))
        
        return ValidationResult(
            file_path=file_path,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=score
        )
    
    def _validate_javascript(self, file_path: str, content: str) -> ValidationResult:
        """Valide un fichier JavaScript"""
        
        errors = []
        warnings = []
        
        if not content.strip():
            errors.append("Fichier vide")
            return ValidationResult(file_path, False, errors, warnings, 0.0)
        
        # Syntaxe de base
        if content.count('{') != content.count('}'):
            errors.append("Déséquilibre d'accolades")
        
        if content.count('(') != content.count(')'):
            errors.append("Déséquilibre de parenthèses")
        
        # Exports
        if 'export' not in content and file_path.endswith('.js'):
            warnings.append("Pas d'exports détectés")
        
        # Console.log en production
        if 'console.log' in content:
            warnings.append("console.log détecté (à retirer en production)")
        
        score = 100.0
        score -= len(errors) * 20
        score -= len(warnings) * 5
        score = max(0, min(100, score))
        
        return ValidationResult(file_path, len(errors) == 0, errors, warnings, score)
    
    def _validate_typescript(self, file_path: str, content: str) -> ValidationResult:
        """Valide un fichier TypeScript"""
        
        # Réutiliser la validation JavaScript avec des vérifications supplémentaires
        result = self._validate_javascript(file_path, content)
        
        # Vérifications TypeScript spécifiques
        if ': any' in content:
            result.warnings.append("Type 'any' détecté (éviter si possible)")
        
        if 'interface' not in content and 'type' not in content:
            result.warnings.append("Pas de types personnalisés définis")
        
        return result
    
    def _validate_tsx(self, file_path: str, content: str) -> ValidationResult:
        """Valide un fichier TSX"""
        # Combiner validations JSX et TypeScript
        result = self._validate_jsx(file_path, content)
        
        if ': any' in content:
            result.warnings.append("Type 'any' détecté")
        
        return result
    
    def _validate_python(self, file_path: str, content: str) -> ValidationResult:
        """Valide un fichier Python"""
        
        errors = []
        warnings = []
        
        if not content.strip():
            errors.append("Fichier vide")
            return ValidationResult(file_path, False, errors, warnings, 0.0)
        
        # Indentation (vérification basique)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.startswith((' ', '\t', '#')):
                # Ligne de code non indentée (peut être OK pour top-level)
                pass
        
        # Imports
        if 'import' not in content:
            warnings.append("Pas d'imports (inhabituel)")
        
        # Fonctions ou classes
        if 'def ' not in content and 'class ' not in content:
            warnings.append("Pas de fonctions ou classes définies")
        
        # Print statements (debug)
        if 'print(' in content and file_path != 'main.py':
            warnings.append("Print statements détectés (debug?)")
        
        # Docstrings
        if '"""' not in content and "'''" not in content:
            warnings.append("Pas de docstrings")
        
        score = 100.0
        score -= len(errors) * 20
        score -= len(warnings) * 5
        score = max(0, min(100, score))
        
        return ValidationResult(file_path, len(errors) == 0, errors, warnings, score)
    
    def _validate_json(self, file_path: str, content: str) -> ValidationResult:
        """Valide un fichier JSON"""
        
        errors = []
        warnings = []
        
        if not content.strip():
            errors.append("Fichier JSON vide")
            return ValidationResult(file_path, False, errors, warnings, 0.0)
        
        # Tenter de parser le JSON
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            errors.append(f"JSON invalide: {str(e)}")
        
        score = 100.0 if len(errors) == 0 else 0.0
        
        return ValidationResult(file_path, len(errors) == 0, errors, warnings, score)
    
    def _validate_html(self, file_path: str, content: str) -> ValidationResult:
        """Valide un fichier HTML"""
        
        errors = []
        warnings = []
        
        if not content.strip():
            errors.append("Fichier HTML vide")
            return ValidationResult(file_path, False, errors, warnings, 0.0)
        
        # DOCTYPE
        if '<!DOCTYPE' not in content and '<!doctype' not in content:
            warnings.append("Pas de DOCTYPE déclaré")
        
        # Balises essentielles
        if '<html' not in content.lower():
            errors.append("Pas de balise <html>")
        
        if '<head' not in content.lower():
            warnings.append("Pas de balise <head>")
        
        if '<body' not in content.lower():
            warnings.append("Pas de balise <body>")
        
        # Meta tags
        if '<meta' not in content.lower():
            warnings.append("Pas de meta tags")
        
        # Title
        if '<title' not in content.lower():
            warnings.append("Pas de <title>")
        
        score = 100.0
        score -= len(errors) * 20
        score -= len(warnings) * 5
        score = max(0, min(100, score))
        
        return ValidationResult(file_path, len(errors) == 0, errors, warnings, score)
    
    def _validate_css(self, file_path: str, content: str) -> ValidationResult:
        """Valide un fichier CSS"""
        
        errors = []
        warnings = []
        
        if not content.strip():
            warnings.append("Fichier CSS vide")
            return ValidationResult(file_path, True, errors, warnings, 80.0)
        
        # Vérifier les accolades
        if content.count('{') != content.count('}'):
            errors.append("Déséquilibre d'accolades CSS")
        
        # Vérifier les point-virgules
        lines = content.split('\n')
        for line in lines:
            if ':' in line and '{' not in line and '}' not in line:
                if not line.strip().endswith((';', '{')):
                    warnings.append("Possible point-virgule manquant")
                    break
        
        score = 100.0
        score -= len(errors) * 20
        score -= len(warnings) * 5
        score = max(0, min(100, score))
        
        return ValidationResult(file_path, len(errors) == 0, errors, warnings, score)
    
    def _validate_generic(self, file_path: str, content: str) -> ValidationResult:
        """Validation générique pour fichiers inconnus"""
        
        warnings = []
        
        if not content.strip():
            warnings.append("Fichier vide")
            return ValidationResult(file_path, True, [], warnings, 50.0)
        
        return ValidationResult(file_path, True, [], warnings, 70.0)
    
    def generate_validation_report(self, results: Dict[str, ValidationResult]) -> str:
        """Génère un rapport de validation"""
        
        total_files = len(results)
        valid_files = sum(1 for r in results.values() if r.is_valid)
        total_errors = sum(len(r.errors) for r in results.values())
        total_warnings = sum(len(r.warnings) for r in results.values())
        overall_score = self.get_project_score(results)
        
        report = f"""
# Rapport de Validation Vectort.io

## Statistiques Globales
- **Score global**: {overall_score:.1f}/100
- **Fichiers validés**: {total_files}
- **Fichiers valides**: {valid_files}/{total_files}
- **Erreurs totales**: {total_errors}
- **Avertissements**: {total_warnings}

## Détails par Fichier

"""
        
        for file_path, result in sorted(results.items()):
            status = "✅" if result.is_valid else "❌"
            report += f"### {status} {file_path} (Score: {result.score:.0f}/100)\n\n"
            
            if result.errors:
                report += "**Erreurs:**\n"
                for error in result.errors:
                    report += f"- ❌ {error}\n"
                report += "\n"
            
            if result.warnings:
                report += "**Avertissements:**\n"
                for warning in result.warnings:
                    report += f"- ⚠️ {warning}\n"
                report += "\n"
        
        return report
