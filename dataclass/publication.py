from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import xml.etree.ElementTree as ET

class Publication(BaseModel):
    id: str
    title: str
    publishedAt: datetime
    channel_id: str
    description: Optional[str] = None

    @classmethod
    def from_xml(cls, xml_string: str) -> 'Publication':
        root = ET.fromstring(xml_string)
        entry = root.find("{http://www.w3.org/2005/Atom}entry")
        publication_data = {
            "id": entry.find("{http://www.youtube.com/xml/schemas/2015}videoId").text,
            "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
            "publishedAt": datetime.strptime(
                entry.find("{http://www.w3.org/2005/Atom}published").text,
                "%Y-%m-%dT%H:%M:%S%z"
            ),
            "channel_id": entry.find("{http://www.youtube.com/xml/schemas/2015}channelId").text,
        }
        return cls(**publication_data)
