import re
from typing import Dict

def evaluate_quality(memory: Dict) -> float:
    """
    Evaluate memory quality based on structural completeness.
    Returns a score between 0.0 and 1.0.
    """
    total_score = 0
    max_score = 7

    if 'title' in memory and memory['title']:
        total_score += 1
    if 'body' in memory and memory['body']:
        total_score += 1
    if 'summary' in memory and memory['summary']:
        total_score += 1
    if 'impulse' in memory and memory['impulse']:
        total_score += 1
    if 'ache' in memory and memory['ache']:
        total_score += 1
    if 'satisfaction' in memory and memory['satisfaction']:
        total_score += 1
    if 'chronology' in memory and isinstance(memory['chronology'], dict):
        if memory['chronology'].get('start') and memory['chronology'].get('end'):
            total_score += 1

    return round(total_score / max_score, 2)

def evaluate_density(summary: str, body: str) -> float:
    """
    Evaluate memory quality based on content length.
    Returns a score between 0.0 and 1.0.
    """
    summary_score = min(len(summary) / 100, 1.0)
    body_score = min(len(body) / 500, 1.0)
    return round((summary_score + body_score) / 2, 2)

def evaluate_overall_quality(memory: Dict) -> float:
    """
    Combine structure and density evaluations.
    """
    structure_score = evaluate_quality(memory)
    summary = memory.get('summary', '')
    body = memory.get('body', '')
    density_score = evaluate_density(summary, body)
    return round((structure_score + density_score) / 2, 2)
