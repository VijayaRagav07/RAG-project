from typing import List, Dict, Any

class RecursiveTextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits a single text string recursively using a list of separators:
        double newlines (paragraphs), single newlines (lines), spaces (words), and characters.
        """
        separators = ["\n\n", "\n", " ", ""]
        return self._split(text, separators)

    def _split(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]
        
        if not separators:
            # Fallback: slice directly if we have run out of separators
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

        separator = separators[0]
        next_separators = separators[1:]
        
        # Check if the separator exists in the text. If not, use the next separator.
        for sep in separators:
            if sep == "":
                separator = sep
                break
            if sep in text:
                separator = sep
                break
        
        splits = text.split(separator) if separator != "" else list(text)
        
        chunks = []
        current_chunk = []
        current_len = 0
        
        for split in splits:
            split_len = len(split)
            
            # If a single split is larger than the chunk size, split it recursively
            if split_len > self.chunk_size:
                if current_chunk:
                    chunks.append(separator.join(current_chunk))
                    current_chunk = []
                    current_len = 0
                
                sub_chunks = self._split(split, next_separators)
                chunks.extend(sub_chunks)
            else:
                # Calculate what the length would be if we added this split
                separator_addition = len(separator) if current_chunk else 0
                if current_len + separator_addition + split_len > self.chunk_size:
                    if current_chunk:
                        chunks.append(separator.join(current_chunk))
                    
                    # Backtrack to build the overlap chunk
                    overlap_chunk = []
                    overlap_len = 0
                    for prev_split in reversed(current_chunk):
                        prev_split_len = len(prev_split)
                        prev_sep_len = len(separator) if overlap_chunk else 0
                        if overlap_len + prev_sep_len + prev_split_len > self.chunk_overlap:
                            break
                        overlap_chunk.insert(0, prev_split)
                        overlap_len += prev_sep_len + prev_split_len
                    
                    current_chunk = overlap_chunk
                    current_len = overlap_len
                
                current_chunk.append(split)
                current_len += (len(separator) if len(current_chunk) > 1 else 0) + split_len
                
        if current_chunk:
            chunks.append(separator.join(current_chunk))
            
        return chunks

    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Splits a list of documents (dictionaries with 'text' and 'metadata') into chunks.
        """
        chunks = []
        for doc in documents:
            text = doc["text"]
            metadata = doc["metadata"]
            text_splits = self.split_text(text)
            for split in text_splits:
                cleaned_split = split.strip()
                if cleaned_split:
                    chunks.append({
                        "text": cleaned_split,
                        "metadata": metadata.copy()
                    })
        return chunks
