import re
from datetime import datetime
from typing import List, Dict, Any

def parse_unavailability_text(text: str) -> List[Dict[str, Any]]:
    """
    Parses the unavailability text format.
    Returns a list of dictionaries with:
    - name: str
    - start_date: datetime
    - end_date: datetime
    - reason: str
    """
    entries = []
    
    # Split by double newlines or just scan through
    # The format seems to be blocks of text.
    # We can try to split by "Nome:" but we need to capture the header before it.
    
    # Strategy:
    # 1. Identify sections. Sections seem to start with a line that is NOT a key-value pair and is followed by "Nome:"
    #    However, "Fériasfe" has numbered entries.
    # 2. Alternatively, just iterate line by line and maintain state.
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    current_reason_header = None
    current_entry = {}
    
    # Regex for date: DD/MM/YYYY HH:MM or DD/MM/YYYY
    date_pattern = r"(\d{2}/\d{2}/\d{4})(?:\s+(\d{2}:\d{2}))?"
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if it's a header (heuristic: doesn't start with known keys and next line is Nome or a number)
        is_key_value = any(line.startswith(k) for k in ["Nome:", "Função:", "Início:", "Fim:", "Descrição:", "Quantidade de dias"])
        is_number = re.match(r"^\d+$", line)
        
        if not is_key_value and not is_number:
            # Legend line - extract last 3 characters as code
            # Examples: "COMISSÃO FISCALIZADORACOM" -> "COM", "RISAERRIS" -> "RIS"
            cleaned_header = line.strip()
            if len(cleaned_header) >= 3:
                current_reason_header = cleaned_header[-3:].upper()
            else:
                current_reason_header = cleaned_header.upper()
            i += 1
            continue
            
        if is_number:
            # Just a counter, skip
            i += 1
            continue
            
        if line.startswith("Nome:"):
            # Start of a new entry
            if current_entry:
                entries.append(current_entry)
            current_entry = {"reason": current_reason_header if current_reason_header else "IND"}
            current_entry["name"] = line.split("Nome:", 1)[1].strip()
        
        elif line.startswith("Início:"):
            val = line.split("Início:", 1)[1].strip()
            match = re.search(date_pattern, val)
            if match:
                d_str = match.group(1)
                t_str = match.group(2) or "00:00"
                current_entry["start"] = datetime.strptime(f"{d_str} {t_str}", "%d/%m/%Y %H:%M")
                
        elif line.startswith("Fim:"):
            val = line.split("Fim:", 1)[1].strip()
            match = re.search(date_pattern, val)
            if match:
                d_str = match.group(1)
                t_str = match.group(2) or "23:59"
                current_entry["end"] = datetime.strptime(f"{d_str} {t_str}", "%d/%m/%Y %H:%M")
                
        elif line.startswith("Descrição:"):
            # If description is present, it overrides the header reason
            desc = line.split("Descrição:", 1)[1].strip()
            if desc:
                current_entry["reason"] = desc
                
        i += 1
        
    if current_entry and "name" in current_entry:
        entries.append(current_entry)
        
    return entries
