from bs4 import BeautifulSoup
from .models import Shift
from datetime import date
import calendar
import re
import logging

logger = logging.getLogger(__name__)

def parse_text_table(text_content: str, month_str: str):
    """
    Parses plain text table (vertical or horizontal format).

    Vertical format (columns - from Excel copy):
    Turno    Quant.   01   02   03
    m        2        2    0    1
    t        2        2    2    3
    p        1        1    1    1

    Horizontal format (rows - from Excel transpose):
    Turno
    m
    t
    p
    Quant.
    2
    2
    1
    01
    2
    2
    1
    """
    lines = [line.strip() for line in text_content.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return []

    year, month = map(int, month_str.split('-'))
    _, last_day = calendar.monthrange(year, month)

    capacity_data = []

    # Map all shift subtypes to their main category
    # We need to SUM all subtypes of each category
    shift_map_manha = ['m', 'm2', 'm3', 'mr', 'mexp', 'msexp']
    shift_map_tarde = ['t', 't2', 't3', 't4', 'tr', 'ic', 'texp']
    shift_map_pernoite = ['p', 'sbm', 'sbt', 'sbp']

    def get_shift_category(label):
        """Returns shift category for all subtypes"""
        label_lower = label.lower().strip()
        if label_lower in shift_map_manha:
            return Shift.manha
        elif label_lower in shift_map_tarde:
            return Shift.tarde
        elif label_lower in shift_map_pernoite:
            return Shift.pernoite
        return None

    # Detect format: vertical (has multiple columns per line) or horizontal (one column)
    # Check first few lines
    first_line_parts = re.split(r'\s+', lines[0])

    if len(first_line_parts) > 2:
        # HORIZONTAL FORMAT (standard table with columns)
        # Special format: Each day has TWO columns (two values)
        # We need the SECOND value of each day
        # Format: Turno | Quant | Day01_val1 Day01_val2 | Day02_val1 Day02_val2 | ...

        # Parse all rows and aggregate by shift category and day
        shift_totals = {}  # {(day, shift): total}

        for line in lines[1:]:  # Skip header
            parts = re.split(r'\s+', line.strip())
            if len(parts) < 4:  # Need at least: Label, Quant, and 2 values for day 1
                continue

            label = parts[0].strip()
            shift = get_shift_category(label)

            if shift:
                # Skip Label (0) and Quant (1), start at index 2
                # Each day has 2 values, we want the second one (odd indices: 3, 5, 7, ...)
                for day in range(1, last_day + 1):
                    # Index for the second value of each day
                    # Day 1: index 3, Day 2: index 5, Day 3: index 7, etc
                    value_index = 2 + (day - 1) * 2 + 1

                    if value_index < len(parts):
                        try:
                            value = int(parts[value_index].strip())
                        except ValueError:
                            value = 0

                        # Accumulate values for this day/shift combination
                        key = (day, shift)
                        shift_totals[key] = shift_totals.get(key, 0) + value

        # Convert aggregated totals to capacity_data
        for (day, shift), total in shift_totals.items():
            capacity_data.append({
                "date": date(year, month, day),
                "shift": shift,
                "total_instructors": total
            })
    else:
        # VERTICAL FORMAT (one value per line - needs transposition)
        # Format: Each turno has 2 values (we want the 2nd one)
        # Structure: Turno, m, m2, M3, MR, t, t2, ..., Quant., [quant values], 01, [day values], 02, ...

        # Find the turno labels (m, t, p positions)
        turno_labels = []
        turno_start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().lower() == 'turno':
                turno_start_idx = i + 1
                break

        # Collect all turno labels until we hit "Quant."
        i = turno_start_idx
        while i < len(lines) and not lines[i].strip().lower().startswith('quant'):
            turno_labels.append(lines[i].strip().lower())
            i += 1

        # Verify we have at least one turno from each category
        has_manha = any(label in shift_map_manha for label in turno_labels)
        has_tarde = any(label in shift_map_tarde for label in turno_labels)
        has_pernoite = any(label in shift_map_pernoite for label in turno_labels)

        if not (has_manha and has_tarde and has_pernoite):
            return []

        # Number of turnos (each with 2 values from HTML divs)
        num_turnos = len(turno_labels)

        # Find the actual "Quant." line
        quant_idx = 0
        for i, line in enumerate(lines):
            if line.lower().startswith('quant'):
                quant_idx = i
                break

        # After Quant. label, there are num_turnos values (NOT * 2!)
        # Quant column has only 1 value per turno, but day columns have 2 values per turno
        # Then comes the first day label
        first_day_label_idx = quant_idx + 1 + num_turnos

        # Process days sequentially
        # Each day block is: day_label + (num_turnos * 2) values
        values_per_day = num_turnos * 2
        day_block_size = 1 + values_per_day

        for day_num in range(1, last_day + 1):
            # Calculate where this day's data should be
            day_idx = first_day_label_idx + ((day_num - 1) * day_block_size)

            # Verify this is actually the day label
            if day_idx >= len(lines):
                break

            day_label = lines[day_idx].strip()
            expected_label = str(day_num).zfill(2)  # "01", "02", etc

            # Check if label matches (could be "1" or "01")
            try:
                parsed_day = int(day_label)
                if parsed_day != day_num:
                    # Day sequence broken, stop processing
                    break
            except ValueError:
                # Not a number, stop processing
                break

            # Sum all subtypes for each category
            manha_total = 0
            tarde_total = 0
            pernoite_total = 0

            for turno_idx, turno_label in enumerate(turno_labels):
                # Get the second value for this turno (the one we want)
                value_idx = day_idx + 1 + (turno_idx * 2) + 1

                if value_idx < len(lines):
                    try:
                        value = int(lines[value_idx].strip())
                    except ValueError:
                        value = 0

                    # Add to the appropriate category
                    shift = get_shift_category(turno_label)
                    if shift == Shift.manha:
                        manha_total += value
                    elif shift == Shift.tarde:
                        tarde_total += value
                    elif shift == Shift.pernoite:
                        pernoite_total += value

            capacity_data.append({
                "date": date(year, month, day_num),
                "shift": Shift.manha,
                "total_instructors": manha_total
            })
            capacity_data.append({
                "date": date(year, month, day_num),
                "shift": Shift.tarde,
                "total_instructors": tarde_total
            })
            capacity_data.append({
                "date": date(year, month, day_num),
                "shift": Shift.pernoite,
                "total_instructors": pernoite_total
            })

    return capacity_data

def parse_html_table(html_content: str, month_str: str):
    """
    Parses the HTML table and returns a list of dictionaries for InstructorCapacity.
    Tries HTML parsing first, falls back to text parsing if HTML tags not found.
    """
    # Check if it's HTML or plain text
    if '<table' in html_content.lower() or '<tr' in html_content.lower():
        # HTML parsing
        soup = BeautifulSoup(html_content, 'html.parser')
        rows = soup.find_all('tr')

        year, month = map(int, month_str.split('-'))
        _, last_day = calendar.monthrange(year, month)

        capacity_data = []

        # Map row labels to Shift enum
        shift_map = {
            'M': Shift.manha,
            'T': Shift.tarde,
            'P': Shift.pernoite
        }

        for row in rows:
            cols = row.find_all(['td', 'th'])
            if not cols:
                continue

            # First column is the label (Turno)
            label = cols[0].get_text(strip=True)

            if label in shift_map:
                shift = shift_map[label]

                # Columns 2 to 32 correspond to days 01 to 31 (index 2 is day 1)
                # The prompt says: Turno | Quant | 01 | 02 ...
                # So index 0 is Turno, index 1 is Quant, index 2 is 01.

                for day in range(1, last_day + 1):
                    col_index = day + 1 # 1st day is at index 2

                    if col_index < len(cols):
                        val_text = cols[col_index].get_text(strip=True)
                        try:
                            total = int(val_text)
                        except ValueError:
                            total = 0

                        capacity_data.append({
                            "date": date(year, month, day),
                            "shift": shift,
                            "total_instructors": total
                        })

        return capacity_data
    else:
        # Plain text parsing
        return parse_text_table(html_content, month_str)
