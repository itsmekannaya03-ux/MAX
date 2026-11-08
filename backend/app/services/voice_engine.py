import re
from typing import Dict, Any, List

class VoiceEngine:
    def __init__(self):
        pass

    def prepare_speech_text(self, text: str) -> str:
        """
        Cleans markdown, code blocks, bold markers, and URLs so speech sounds 100% natural.
        """
        # Remove markdown code blocks
        clean = re.sub(r'```[\s\S]*?```', 'Here is a code example shown on screen.', text)
        clean = re.sub(r'`([^`]+)`', r'\1', clean)
        # Remove links
        clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)
        clean = re.sub(r'http[s]?://\S+', '', clean)
        # Remove bold/italic markers
        clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)
        clean = re.sub(r'\*([^*]+)\*', r'\1', clean)
        # Remove markdown headers and bullets
        clean = re.sub(r'#+\s*', '', clean)
        clean = re.sub(r'^\s*[-*+]\s+', '', clean, flags=re.MULTILINE)
        # Condense extra spaces
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

voice_engine = VoiceEngine()

