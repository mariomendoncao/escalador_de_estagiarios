# Migration Guide - Month-Based Isolation

## Overview

The application has been completely refactored to support **month-based data isolation**. Now each month has its own set of:
- Trainees (estagiários)
- Availability (indisponibilidades)
- Instructor Capacity (capacidade de instrutores)
- Schedule/Assignments (escala gerada)

## Database Changes

### New Schema

A new table `monthly_schedules` has been added as the central context for each month:

```sql
monthly_schedules
  - id
  - month (YYYY-MM, unique)
  - created_at

trainees (updated)
  - id
  - monthly_schedule_id (FK)
  - name
  - active
  - created_at
  - UNIQUE(monthly_schedule_id, name)

trainee_availability (updated)
  - id
  - monthly_schedule_id (FK)
  - trainee_id (FK)
  - date
  - shift
  - available

instructor_capacity (updated)
  - id
  - monthly_schedule_id (FK)
  - date
  - shift
  - total_instructors

trainee_assignments (updated)
  - id
  - monthly_schedule_id (FK)
  - trainee_id (FK)
  - date
  - shift
```

## Migration Steps

### 1. Reset the Database

**WARNING: This will delete all existing data!**

```bash
cd backend
python reset_database.py
```

Or manually using Docker:

```bash
docker-compose down
docker volume rm escala_estagiarios_db_data  # Adjust volume name as needed
docker-compose up -d
```

### 2. Restart Backend

```bash
cd backend
# Restart your backend server
```

### 3. Restart Frontend

```bash
cd frontend
npm run dev
```

## New Workflow

### Step 1: Select/Create Month
1. Open the application
2. On the main page, you'll see "Select a Month to Work On"
3. Either:
   - Create a new month using the date picker
   - Select an existing month from the list
4. Click "Work on this Month"

### Step 2: Import Data
After selecting a month, you'll be redirected to the Import page where you can:

#### Import Trainees & Availability
Paste JSON in this format:
```json
{
  "1S SOLANGE": {
    "06": "RIS",
    "07": "RIS",
    "22": "SbRi"
  },
  "3S ANDRADE": {
    "11": "SbRi",
    "23": "RIS",
    "24": "RIS",
    "31": "SbRi"
  }
}
```

**Important:** Days listed in the JSON are **UNAVAILABLE**. Days not listed are **AVAILABLE**.

#### Import Instructor Capacity
Paste the HTML table content with capacity for each shift and day.

### Step 3: Work with the Data
Navigate to:
- **Trainees**: View/edit trainees for the selected month
- **Availability**: Fine-tune individual trainee availability
- **Schedule**: Generate and view the schedule

### Step 4: Generate Schedule
On the Schedule page:
1. Click "Gerar Escala" to generate assignments
2. View the generated schedule
3. Export to CSV if needed

## API Changes

All API endpoints now require a `month` parameter in the URL path:

### Old Endpoints
```
GET  /trainees
POST /trainees
GET  /schedule?month=2025-01
POST /schedule/generate
```

### New Endpoints
```
GET  /months                                    # List all months
POST /months                                    # Create a month
DELETE /months/{month}                          # Delete a month

GET  /months/{month}/trainees                   # Get trainees for month
POST /months/{month}/trainees                   # Create trainee for month
POST /months/{month}/trainees/bulk-import       # Import trainees + availability

GET  /months/{month}/trainees/{id}/availability
POST /months/{month}/trainees/{id}/availability/bulk

POST /months/{month}/instructor-capacity/import
GET  /months/{month}/instructor-capacity

POST /months/{month}/schedule/generate
GET  /months/{month}/schedule
```

## Benefits of This Approach

1. **Complete Isolation**: Each month is independent. Deleting a month removes all its data.
2. **Different Trainees per Month**: You can have different sets of trainees in each month.
3. **Historical Data**: Keep multiple months without conflicts.
4. **Clearer Workflow**: Select month first, then work on that month's data.
5. **Easier Management**: Delete an entire month with one click.

## Troubleshooting

### "No month selected" error
- Make sure you select a month from the home page first
- The selected month is stored in localStorage

### Trainees not showing up
- Ensure you're looking at the correct month
- Verify the month is created in the database

### Import fails
- Check JSON format (must be valid JSON)
- Ensure month is selected
- Check browser console for detailed errors

## Frontend State Management

The selected month is stored in `localStorage` with the key `selectedMonth`. This persists across page refreshes. To manually clear:

```javascript
localStorage.removeItem('selectedMonth')
```

## Code Structure

### Backend
- `models.py`: Updated with MonthlySchedule model and relationships
- `schemas.py`: Added MonthlySchedule schemas and BulkImportRequest
- `crud.py`: All CRUD operations now accept `month` parameter
- `routers/trainees.py`: Updated endpoints with `/months/{month}` prefix
- `routers/schedule.py`: Month management and schedule endpoints
- `scheduler.py`: Updated to work with month-specific data

### Frontend
- `views/MonthSelection.vue`: New - Select/create/delete months
- `views/Import.vue`: New - Unified import page for trainees and capacity
- `views/Trainees.vue`: Updated - Works with selected month context
- `views/Availability.vue`: Updated - Works with selected month context
- `views/Schedule.vue`: Updated - Works with selected month context
- `router/index.js`: Updated routes
- `App.vue`: Updated navigation menu

## Next Steps

After migration:
1. Create a month (e.g., "2025-01")
2. Import your trainee data using the JSON format
3. Import instructor capacity
4. Generate the schedule
5. Export or view the results

If you need to work on a different month, simply go back to the home page and select/create another month.
