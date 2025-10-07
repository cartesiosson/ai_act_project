#!/usr/bin/env python3
"""
Script para analizar la internacionalización de la ontología AI Act
Detecta términos sin traducción completa o con problemas de traducción
"""

import re
from collections import defaultdict

def analyze_ontology_i18n(file_path):
    """Analiza la internacionalización de una ontología Turtle"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrones para encontrar etiquetas y comentarios
    label_pattern = r'(\w+:\w+)\s+a\s+[\w:]+.*?(?=\n\w+:|$)'
    rdfs_label_pattern = r'rdfs:label\s+"([^"]+)"@(en|es)'
    rdfs_comment_pattern = r'rdfs:comment\s+"([^"]+)"@(en|es)'
    
    # Estructura para almacenar los resultados
    entities = defaultdict(lambda: {'labels': {}, 'comments': {}, 'line_numbers': []})
    
    # Encontrar todas las entidades y sus metadatos
    lines = content.split('\n')
    current_entity = None
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        # Identificar nueva entidad
        entity_match = re.match(r'^(\w+:\w+)\s+a\s+', line)
        if entity_match:
            current_entity = entity_match.group(1)
            entities[current_entity]['line_numbers'].append(i)
        
        # Encontrar etiquetas
        label_matches = re.findall(rdfs_label_pattern, line)
        for text, lang in label_matches:
            if current_entity:
                entities[current_entity]['labels'][lang] = text
        
        # Encontrar comentarios
        comment_matches = re.findall(rdfs_comment_pattern, line)
        for text, lang in comment_matches:
            if current_entity:
                entities[current_entity]['comments'][lang] = text
    
    # Analizar problemas
    problems = {
        'missing_spanish_labels': [],
        'missing_english_labels': [],
        'missing_spanish_comments': [],
        'missing_english_comments': [],
        'potential_translation_issues': []
    }
    
    for entity, data in entities.items():
        # Problemas con etiquetas
        if 'en' in data['labels'] and 'es' not in data['labels']:
            problems['missing_spanish_labels'].append({
                'entity': entity,
                'english': data['labels']['en'],
                'lines': data['line_numbers']
            })
        
        if 'es' in data['labels'] and 'en' not in data['labels']:
            problems['missing_english_labels'].append({
                'entity': entity,
                'spanish': data['labels']['es'],
                'lines': data['line_numbers']
            })
        
        # Problemas con comentarios
        if 'en' in data['comments'] and 'es' not in data['comments']:
            problems['missing_spanish_comments'].append({
                'entity': entity,
                'english': data['comments']['en'],
                'lines': data['line_numbers']
            })
        
        if 'es' in data['comments'] and 'en' not in data['comments']:
            problems['missing_english_comments'].append({
                'entity': entity,
                'spanish': data['comments']['es'],
                'lines': data['line_numbers']
            })
        
        # Revisar posibles problemas de traducción
        if 'en' in data['labels'] and 'es' in data['labels']:
            en_label = data['labels']['en'].lower()
            es_label = data['labels']['es'].lower()
            
            # Detectar traducciones potencialmente problemáticas
            if en_label == es_label:  # Mismo texto en ambos idiomas
                problems['potential_translation_issues'].append({
                    'entity': entity,
                    'issue': 'identical_text',
                    'en': data['labels']['en'],
                    'es': data['labels']['es'],
                    'lines': data['line_numbers']
                })
    
    return problems, entities

def print_report(problems, entities):
    """Imprime un reporte detallado de los problemas encontrados"""
    
    print("=== ANÁLISIS DE INTERNACIONALIZACIÓN DE LA ONTOLOGÍA AI ACT ===\n")
    
    # Estadísticas generales
    total_entities = len(entities)
    entities_with_both_labels = sum(1 for e in entities.values() if 'en' in e['labels'] and 'es' in e['labels'])
    entities_with_both_comments = sum(1 for e in entities.values() if 'en' in e['comments'] and 'es' in e['comments'])
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total de entidades: {total_entities}")
    print(f"   Entidades con etiquetas en ambos idiomas: {entities_with_both_labels}/{total_entities}")
    print(f"   Entidades con comentarios en ambos idiomas: {entities_with_both_comments}/{total_entities}")
    print()
    
    # Problemas encontrados
    if problems['missing_spanish_labels']:
        print("❌ ETIQUETAS FALTANTES EN ESPAÑOL:")
        for item in problems['missing_spanish_labels']:
            print(f"   • {item['entity']} (líneas {item['lines']})")
            print(f"     EN: \"{item['english']}\"")
            print(f"     ES: ❌ FALTA")
        print()
    
    if problems['missing_english_labels']:
        print("❌ ETIQUETAS FALTANTES EN INGLÉS:")
        for item in problems['missing_english_labels']:
            print(f"   • {item['entity']} (líneas {item['lines']})")
            print(f"     EN: ❌ FALTA")
            print(f"     ES: \"{item['spanish']}\"")
        print()
    
    if problems['missing_spanish_comments']:
        print("⚠️  COMENTARIOS FALTANTES EN ESPAÑOL:")
        for item in problems['missing_spanish_comments']:
            print(f"   • {item['entity']} (líneas {item['lines']})")
            print(f"     EN: \"{item['english'][:80]}...\"")
            print(f"     ES: ❌ FALTA")
        print()
    
    if problems['missing_english_comments']:
        print("⚠️  COMENTARIOS FALTANTES EN INGLÉS:")
        for item in problems['missing_english_comments']:
            print(f"   • {item['entity']} (líneas {item['lines']})")
            print(f"     EN: ❌ FALTA")
            print(f"     ES: \"{item['spanish'][:80]}...\"")
        print()
    
    if problems['potential_translation_issues']:
        print("🔍 POSIBLES PROBLEMAS DE TRADUCCIÓN:")
        for item in problems['potential_translation_issues']:
            print(f"   • {item['entity']} (líneas {item['lines']})")
            print(f"     Problema: {item['issue']}")
            print(f"     EN: \"{item['en']}\"")
            print(f"     ES: \"{item['es']}\"")
        print()
    
    # Resumen de problemas
    total_problems = (len(problems['missing_spanish_labels']) + 
                     len(problems['missing_english_labels']) + 
                     len(problems['missing_spanish_comments']) + 
                     len(problems['missing_english_comments']) + 
                     len(problems['potential_translation_issues']))
    
    print(f"📝 RESUMEN:")
    print(f"   Total de problemas encontrados: {total_problems}")
    print(f"   - Etiquetas sin traducir al español: {len(problems['missing_spanish_labels'])}")
    print(f"   - Etiquetas sin traducir al inglés: {len(problems['missing_english_labels'])}")
    print(f"   - Comentarios sin traducir al español: {len(problems['missing_spanish_comments'])}")
    print(f"   - Comentarios sin traducir al inglés: {len(problems['missing_english_comments'])}")
    print(f"   - Posibles problemas de traducción: {len(problems['potential_translation_issues'])}")

if __name__ == "__main__":
    ontology_file = "/home/cartesio/workspace/FTM/ai_act_project/ontologias/versions/0.36.0/ontologia-v0.36.0.ttl"
    problems, entities = analyze_ontology_i18n(ontology_file)
    print_report(problems, entities)