from agentforge.tools.semantic_chunk import semantic_chunk
from agentforge.tools.get_text import GetText
from agentforge.storage.chroma_storage import ChromaStorage
import os

gettext_instance = GetText()
folder = '../docs'
storage = ChromaStorage('dignity')


def list_files(directory):
    with os.scandir(directory) as entries:
        return [entry.path for entry in entries if entry.is_file()]


files = list_files(folder)
for file in files:
    text = gettext_instance.read_file(file)
    chunks = semantic_chunk(text)
    for chunk in chunks:
        source_id = storage.count_collection('docs')
        source_id_string = [str(source_id + 1)]
        position = chunks.index(chunk)
        content = chunk.content
        metadata = {
            "Source": file,
            "Position": position
        }
        storage.save_memory(collection_name='docs', data=content, ids=source_id_string, metadata=[metadata])
        print(f"Data: {content}\nID: {source_id_string}\nPosition: {position}")
