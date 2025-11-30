<template>
  <div class="w-full bg-slate-50 min-h-screen">
    <!-- Header Section -->
    <div class="bg-white shadow-sm border-b border-slate-200 px-4 py-3">
      <div class="flex flex-col sm:flex-row justify-between items-center gap-4">
        <div class="flex items-center space-x-4">
          <label for="month" class="block text-xs font-bold text-slate-700 uppercase tracking-wide">Mês de Referência</label>
          <input 
            type="month" 
            id="month" 
            v-model="month" 
            @change="fetchData" 
            class="focus:ring-indigo-500 focus:border-indigo-500 block shadow-sm text-xs border-slate-300 rounded px-2 py-1"
          >
        </div>
        <div class="flex flex-wrap gap-2">
          <button @click="generateSchedule" class="inline-flex items-center justify-center py-1.5 px-3 border border-transparent shadow-sm text-xs font-medium rounded text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
            <span class="mr-1">⚡</span> Gerar
          </button>
          <button @click="clearSchedule" class="inline-flex items-center justify-center py-1.5 px-3 border border-transparent shadow-sm text-xs font-medium rounded text-white bg-rose-600 hover:bg-rose-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-rose-500 transition-colors">
            <span class="mr-1">🗑️</span> Limpar
          </button>
          <button @click="exportCSV" class="inline-flex items-center justify-center py-1.5 px-3 border border-slate-300 shadow-sm text-xs font-medium rounded text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
            <span class="mr-1">📥</span> Exportar
          </button>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="bg-white border-b border-slate-200 px-4">
      <nav class="-mb-px flex space-x-6" aria-label="Tabs">
        <button
          @click="currentTab = 'schedule'"
          :class="[
            currentTab === 'schedule'
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300',
            'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-xs transition-colors'
          ]"
        >
          📅 Escala
        </button>
        <button
          @click="currentTab = 'parameters'"
          :class="[
            currentTab === 'parameters'
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300',
            'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-xs transition-colors'
          ]"
        >
          ⚙️ Parâmetros
        </button>
      </nav>
    </div>

    <!-- Schedule View -->
    <div v-if="currentTab === 'schedule'" class="w-full">
      
      <!-- Main Schedule Table with Integrated Capacity -->
      <div class="bg-white shadow-sm border-b border-slate-300 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-300 border-collapse table-fixed">
            <thead>
              <!-- Month/Days Header -->
              <tr class="bg-slate-50">
                <th class="sticky left-0 z-20 bg-slate-50 px-2 py-2 text-left text-[10px] font-bold text-slate-600 uppercase tracking-wider border-b border-r border-slate-300 w-48">
                  Estagiário
                </th>
                <th 
                  v-for="day in days" 
                  :key="day.date" 
                  class="px-1 py-1 text-center text-[10px] font-semibold text-slate-700 border-b border-r border-slate-300 w-8"
                  :class="{'bg-purple-50 text-purple-800': isWeekend(day.date)}"
                >
                  <div class="flex flex-col items-center leading-tight">
                    <span>{{ day.day }}</span>
                    <span class="text-[9px] opacity-75">{{ getDayOfWeekShort(day.date) }}</span>
                  </div>
                </th>
                <th class="px-2 py-2 text-center text-[10px] font-bold text-slate-600 uppercase tracking-wider border-b border-slate-300 w-12">
                  Total
                </th>
              </tr>

              <!-- Capacity Rows (Integrated) -->
              <!-- Manhã -->
              <tr class="bg-slate-50/50">
                <th class="sticky left-0 z-10 bg-slate-50/90 px-2 py-1 text-right text-[10px] font-medium text-slate-600 border-b border-r border-slate-200">
                  Instr. (M)
                </th>
                <td 
                  v-for="day in days" 
                  :key="`cap-m-${day.date}`" 
                  class="px-0 py-1 text-center text-[10px] font-bold text-slate-600 border-b border-r border-slate-200"
                  :class="{'bg-slate-100/50': isWeekend(day.date)}"
                >
                  {{ getRawInstructorCount(day.date, 'manha') }}
                </td>
                <td class="bg-slate-50 border-b border-slate-300"></td>
              </tr>
              <!-- Tarde -->
              <tr class="bg-slate-50/50">
                <th class="sticky left-0 z-10 bg-slate-50/90 px-2 py-1 text-right text-[10px] font-medium text-slate-600 border-b border-r border-slate-200">
                  Instr. (T)
                </th>
                <td 
                  v-for="day in days" 
                  :key="`cap-t-${day.date}`" 
                  class="px-0 py-1 text-center text-[10px] font-bold text-slate-600 border-b border-r border-slate-200"
                  :class="{'bg-slate-100/50': isWeekend(day.date)}"
                >
                  {{ getRawInstructorCount(day.date, 'tarde') }}
                </td>
                <td class="bg-slate-50 border-b border-slate-300"></td>
              </tr>
              <!-- Pernoite -->
              <tr class="bg-slate-50/50">
                <th class="sticky left-0 z-10 bg-slate-50/90 px-2 py-1 text-right text-[10px] font-medium text-slate-600 border-b border-r border-slate-200">
                  Instr. (P)
                </th>
                <td 
                  v-for="day in days" 
                  :key="`cap-p-${day.date}`" 
                  class="px-0 py-1 text-center text-[10px] font-bold text-slate-600 border-b border-r border-slate-200"
                  :class="{'bg-slate-100/50': isWeekend(day.date)}"
                >
                  {{ getRawInstructorCount(day.date, 'pernoite') }}
                </td>
                <td class="bg-slate-50 border-b border-slate-300"></td>
              </tr>

              <!-- Escalados / Vagas Summary -->
              <tr class="bg-slate-100">
                <th class="sticky left-0 z-10 bg-slate-100 px-2 py-2 text-right text-[10px] font-bold text-slate-700 border-b border-r border-slate-300">
                  Escalados / Vagas
                </th>
                <td 
                  v-for="day in days" 
                  :key="`summary-${day.date}`" 
                  class="px-0 py-1 border-b border-r border-slate-300"
                >
                  <div class="flex flex-col items-center space-y-0.5">
                    <div :class="getSummaryClass(day.date, 'manha')" class="rounded px-0.5 w-full text-center text-[10px] font-bold">{{ getShiftCount(day.date, 'manha') }}</div>
                    <div :class="getSummaryClass(day.date, 'tarde')" class="rounded px-0.5 w-full text-center text-[10px] font-bold">{{ getShiftCount(day.date, 'tarde') }}</div>
                    <div :class="getSummaryClass(day.date, 'pernoite')" class="rounded px-0.5 w-full text-center text-[10px] font-bold">{{ getShiftCount(day.date, 'pernoite') }}</div>
                  </div>
                </td>
                <td class="bg-slate-50 border-b border-slate-300"></td>
              </tr>

              <!-- Duplicated Month/Days Header -->
              <tr class="bg-slate-50">
                <th class="sticky left-0 z-20 bg-slate-50 px-2 py-2 text-left text-[10px] font-bold text-slate-600 uppercase tracking-wider border-b border-r border-slate-300 w-48">
                  Estagiário
                </th>
                <th 
                  v-for="day in days" 
                  :key="`dup-header-${day.date}`" 
                  class="px-1 py-1 text-center text-[10px] font-semibold text-slate-700 border-b border-r border-slate-300 w-8"
                  :class="{'bg-purple-50 text-purple-800': isWeekend(day.date)}"
                >
                  <div class="flex flex-col items-center leading-tight">
                    <span>{{ day.day }}</span>
                    <span class="text-[9px] opacity-75">{{ getDayOfWeekShort(day.date) }}</span>
                  </div>
                </th>
                <th class="px-2 py-2 text-center text-[10px] font-bold text-slate-600 uppercase tracking-wider border-b border-slate-300 w-12">
                  Total
                </th>
              </tr>
            </thead>
            
            <tbody class="bg-white divide-y divide-slate-300">
              <tr v-for="trainee in trainees" :key="trainee.id" class="hover:bg-slate-50 transition-colors">
                <td class="sticky left-0 z-10 bg-white px-2 py-1 whitespace-nowrap text-xs font-medium text-slate-900 border-r border-slate-300 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)]">
                  {{ trainee.name }}
                </td>
                <td 
                  v-for="day in days" 
                  :key="`${trainee.id}-${day.date}`" 
                  class="px-0 py-0 text-center border-r border-slate-300 relative h-8 w-8 p-0"
                  :class="{
                    'bg-purple-50': isWeekend(day.date),
                    'bg-red-50': isUnavailable(trainee.id, day.date)
                  }"
                >
                  <div 
                    class="w-full h-full flex items-center justify-center text-xs cursor-pointer hover:bg-blue-50 transition-colors"
                    @click="handleCellClick($event, trainee.id, day.date)"
                  >
                    <!-- Loading Spinner -->
                    <div v-if="loadingCell === `${trainee.id}-${day.date}`" class="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
                    
                    <!-- Show both shift and unavailability if both exist -->
                    <div v-else-if="getAssignment(trainee.id, day.date) && isUnavailable(trainee.id, day.date)" class="flex flex-col items-center leading-none">
                      <span :class="getShiftClass(getAssignment(trainee.id, day.date))">
                        {{ getAssignment(trainee.id, day.date) }}
                      </span>
                      <span class="text-red-600 text-[8px] font-bold tracking-tighter mt-0.5">{{ getUnavailabilityReason(trainee.id, day.date) }}</span>
                    </div>
                    
                    <!-- Shift Content only -->
                    <span v-else-if="getAssignment(trainee.id, day.date)" :class="getShiftClass(getAssignment(trainee.id, day.date))">
                      {{ getAssignment(trainee.id, day.date) }}
                    </span>
                    
                    <!-- Unavailable only -->
                    <span v-else-if="isUnavailable(trainee.id, day.date)" class="text-red-600 text-[9px] font-bold tracking-tighter">{{ getUnavailabilityReason(trainee.id, day.date) }}</span>
                  </div>
                </td>
                <td class="px-2 py-1 whitespace-nowrap text-center text-xs font-bold text-slate-700">
                  {{ getTraineeTotal(trainee.id) }}
                </td>
              </tr>
            </tbody>


          </table>
        </div>
      </div>

      <!-- Dropdown Menu -->
      <div 
        v-if="editingCell" 
        class="fixed z-50 bg-white shadow-xl rounded border border-slate-200 py-1 w-28 transform transition-all duration-200 ease-out"
        :style="{ top: dropdownPosition.top + 'px', left: dropdownPosition.left + 'px' }"
      >
        <button 
          v-for="option in shiftOptions" 
          :key="option.value"
          @click="setShift(option.value)"
          class="block w-full text-left px-3 py-1.5 text-xs text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
        >
          {{ option.label }}
        </button>
        <button
          v-if="getCurrentShift()"
          @click="clearShift"
          class="w-full px-3 py-1.5 text-left hover:bg-red-50 text-xs font-medium text-red-600 border-t border-gray-200"
        >
          Limpar
        </button>
      </div>
  
      <!-- Click-away overlay -->
      <div
        v-if="editingCell"
        class="fixed inset-0 z-40"
        @click="closeDropdown"
      ></div>
    </div>

    <!-- Parameters View -->
    <div v-if="currentTab === 'parameters'">
      <ScheduleParameters :month="month" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import ScheduleParameters from '../components/ScheduleParameters.vue';

const router = useRouter();
const currentTab = ref('schedule');
const month = ref(new Date().toISOString().slice(0, 7));
const schedule = ref([]);
const trainees = ref([]);
const capacities = ref([]);
const availabilities = ref([]);
const editingCell = ref(null);
const dropdownPosition = ref({ top: 0, left: 0 });
const loadingCell = ref(null);

const shiftOptions = [
  { value: 'manha', label: 'M - Manhã' },
  { value: 'tarde', label: 'T - Tarde' },
  { value: 'pernoite', label: 'P - Pernoite' }
];

const days = computed(() => {
  if (!month.value) return [];
  const [y, m] = month.value.split('-').map(Number);
  const date = new Date(y, m, 0);
  const daysInMonth = date.getDate();
  const result = [];
  const weekdays = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sab'];
  
  for (let i = 1; i <= daysInMonth; i++) {
    const d = new Date(y, m - 1, i);
    const dateStr = d.toISOString().slice(0, 10);
    result.push({
      date: dateStr,
      day: i,
      weekday: weekdays[d.getDay()]
    });
  }
  return result;
});

const fetchData = async () => {
  const selectedMonth = localStorage.getItem('selectedMonth');
  if (selectedMonth) {
    month.value = selectedMonth;
  }

  if (!month.value) {
    alert('No month selected. Please select a month first.');
    router.push('/');
    return;
  }

  try {
    const [traineesRes, scheduleRes, capacitiesRes, availabilitiesRes] = await Promise.all([
      api.get(`/months/${month.value}/trainees`),
      api.get(`/months/${month.value}/schedule`),
      api.get(`/months/${month.value}/instructor-capacity`),
      api.get(`/months/${month.value}/availability`)
    ]);
    trainees.value = traineesRes.data.filter(t => t.active); // Only show active trainees
    schedule.value = scheduleRes.data;
    capacities.value = capacitiesRes.data;
    availabilities.value = availabilitiesRes.data;
  } catch (e) {
    console.error('Error fetching data:', e);
    if (e.response && e.response.status === 404) {
      alert('Selected month no longer exists. Please select another month.');
      localStorage.removeItem('selectedMonth');
      router.push('/');
    }
  }
};

const generateSchedule = async () => {
  if (confirm('Isso irá sobrescrever a escala existente para este mês. Continuar?')) {
    try {
      await api.post(`/months/${month.value}/schedule/generate`);
      fetchData();
    } catch (e) {
      alert('Erro ao gerar escala');
    }
  }
};

const clearSchedule = async () => {
  if (confirm('Isso irá limpar toda a escala para este mês. Continuar?')) {
    try {
      await api.delete(`/months/${month.value}/schedule`);
      fetchData();
    } catch (e) {
      alert('Erro ao limpar escala');
    }
  }
};

const clearTraineeSchedule = async (traineeId) => {
  const trainee = trainees.value.find(t => t.id === traineeId);
  const traineeName = trainee ? trainee.name : traineeId;
  if (confirm(`Limpar escala de ${traineeName}?`)) {
    try {
      await api.delete(`/months/${month.value}/trainees/${traineeId}/schedule`);
      fetchData();
    } catch (e) {
      alert('Erro ao limpar escala do estagiário');
    }
  }
};

const getShift = (traineeId, date) => {
  const entry = schedule.value.find(s => s.trainee_id === traineeId && s.date === date);
  return entry ? entry.shift : null;
};

const isUnavailable = (traineeId, date) => {
  // Check if trainee is unavailable on this date for any shift
  const unavail = availabilities.value.find(a => {
    // Normalize both dates to YYYY-MM-DD format for comparison
    const availDate = typeof a.date === 'string'
      ? a.date.slice(0, 10)
      : new Date(a.date).toISOString().slice(0, 10);

    return a.trainee_id === traineeId &&
      availDate === date &&
      !a.available;
  });
  return !!unavail;
};

const getUnavailabilityReason = (traineeId, date) => {
  // Get the reason for unavailability on this date
  const unavail = availabilities.value.find(a => {
    // Normalize both dates to YYYY-MM-DD format for comparison
    const availDate = typeof a.date === 'string'
      ? a.date.slice(0, 10)
      : new Date(a.date).toISOString().slice(0, 10);

    return a.trainee_id === traineeId &&
      availDate === date &&
      !a.available;
  });
  if (!unavail) return null;

  // Extract first 3 characters and convert to uppercase
  const reason = unavail.reason || 'IND';
  return reason.substring(0, 3).toUpperCase();
};

const getCellContent = (traineeId, date) => {
  const shift = getShift(traineeId, date);
  if (shift) {
    return getShiftCode(shift);
  }
  if (isUnavailable(traineeId, date)) {
    return getUnavailabilityReason(traineeId, date);
  }
  return '';
};

const getCellClass = (traineeId, date) => {
  const classes = [];

  if (isWeekend(date)) {
    classes.push('bg-green-100');
  }

  if (isUnavailable(traineeId, date) && !getShift(traineeId, date)) {
    classes.push('bg-red-200');
  }

  // Highlight if currently editing
  if (editingCell.value?.traineeId === traineeId && editingCell.value?.date === date) {
    classes.push('ring-2 ring-indigo-500 bg-indigo-50');
  } else if (!isUnavailable(traineeId, date)) {
    classes.push('hover:bg-blue-50 hover:border-indigo-300');
  }

  return classes.join(' ');
};

const getShiftCode = (shift) => {
  if (!shift) return '';
  const codes = {
    'manha': 'M',
    'tarde': 'T',
    'pernoite': 'P'
  };
  return codes[shift] || shift.charAt(0).toUpperCase();
};

const getShiftColor = (shift) => {
  if (!shift) return '';
  // Example colors based on shift type if needed, currently just black
  return 'text-gray-900';
};

const getTraineeDayCount = (traineeId) => {
  return schedule.value.filter(s => s.trainee_id === traineeId).length;
};

const getShiftCount = (date, shift) => {
  const assigned = schedule.value.filter(s => s.date === date && s.shift === shift).length;
  const capacity = getCapacity(date, shift);
  return `${assigned}/${capacity}`;
};

const getRawInstructorCount = (date, shift) => {
  const cap = capacities.value.find(c => c.date === date && c.shift === shift);
  return cap ? cap.total_instructors : 0;
};

const getCapacity = (date, shift) => {
  const totalInstructors = getRawInstructorCount(date, shift);
  return Math.ceil(totalInstructors / 2);
};

const isWeekend = (dateStr) => {
  // Create date object and adjust for timezone if necessary, or just use UTC to avoid shifts
  // App uses YYYY-MM-DD strings.
  const [year, month, day] = dateStr.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday
  return dayOfWeek === 0 || dayOfWeek === 6;
};

const getMonthName = (monthStr) => {
  if (!monthStr) return '';
  const [y, m] = monthStr.split('-');
  const date = new Date(y, m - 1, 1);
  return date.toLocaleString('pt-BR', { month: 'long', year: 'numeric' }).toUpperCase();
};

const getDayOfWeekShort = (dateStr) => {
  const [year, month, day] = dateStr.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
  return weekdays[date.getDay()];
};

const getAssignment = (traineeId, date) => {
  const assignment = schedule.value.find(s => s.trainee_id === traineeId && s.date === date);
  if (!assignment) return '';
  
  const shiftMap = {
    'manha': 'M',
    'tarde': 'T',
    'pernoite': 'P'
  };
  return shiftMap[assignment.shift] || '';
};

const getShiftClass = (shift) => {
  const classes = {
    'M': 'text-blue-700 font-bold bg-blue-100 px-1 rounded',
    'T': 'text-blue-700 font-bold bg-blue-100 px-1 rounded',
    'P': 'text-blue-700 font-bold bg-blue-100 px-1 rounded'
  };
  return classes[shift] || '';
};

const getTraineeTotal = (traineeId) => {
  return schedule.value.filter(s => s.trainee_id === traineeId).length;
};

const getSummaryClass = (date, shift) => {
  const assigned = parseInt(getShiftCount(date, shift).split('/')[0]);
  const capacity = getCapacity(date, shift);
  
  if (assigned < capacity) return 'text-amber-600 bg-amber-100';
  if (assigned === capacity) return 'text-green-600 bg-green-100';
  return 'text-red-600 bg-red-100';
};

const exportCSV = () => {
  let csv = 'Estagiário';
  days.value.forEach(d => {
    csv += `,${d.day}/${d.weekday}`;
  });
  csv += '\n';

  trainees.value.forEach(t => {
    csv += `"${t.name}"`;
    days.value.forEach(d => {
      const content = getCellContent(t.id, d.date);
      csv += `,${content}`;
    });
    csv += '\n';
  });

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `escala-${month.value}.csv`;
  a.click();
};

const handleCellClick = (event, traineeId, date) => {
  // Allow editing even if unavailable
  // if (isUnavailable(traineeId, date)) {
  //   return;
  // }

  // Calculate dropdown position below or above the cell
  const cell = event.currentTarget;
  const rect = cell.getBoundingClientRect();
  
  // Check if cell is in the lower half of the viewport
  const viewportHeight = window.innerHeight;
  const isInLowerHalf = rect.bottom > viewportHeight / 2;
  
  // Estimated dropdown height (approximate based on number of options)
  const dropdownHeight = shiftOptions.length * 40 + 50; // ~40px per option + padding
  
  dropdownPosition.value = {
    top: isInLowerHalf 
      ? rect.top - dropdownHeight - 2  // Position above the cell
      : rect.bottom + 2,                // Position below the cell
    left: rect.left                     // Align with the left edge of the cell
  };

  editingCell.value = { traineeId, date };
};

const canEdit = (traineeId, date) => {
  return !isUnavailable(traineeId, date);
};

const isLoading = (traineeId, date) => {
  return loadingCell.value?.traineeId === traineeId && loadingCell.value?.date === date;
};

const getCurrentShift = () => {
  if (!editingCell.value) return null;
  return getShift(editingCell.value.traineeId, editingCell.value.date);
};

const closeDropdown = () => {
  editingCell.value = null;
};

const setShift = async (shift) => {
  if (!editingCell.value) return;

  const { traineeId, date } = editingCell.value;
  
  // Close dropdown immediately for instant feedback
  closeDropdown();
  
  // Set loading state
  loadingCell.value = `${traineeId}-${date}`;

  try {
    await api.post(
      `/months/${month.value}/trainees/${traineeId}/assignments`,
      { date, shift }
    );

    await fetchData();
  } catch (error) {
    console.error('Error setting shift:', error);
    alert('Error setting shift');
  } finally {
    // Clear loading state
    loadingCell.value = null;
  }
};

const clearShift = async () => {
  if (!editingCell.value) return;

  const { traineeId, date } = editingCell.value;
  
  // Close dropdown immediately for instant feedback
  closeDropdown();
  
  // Set loading state
  loadingCell.value = { traineeId, date };

  try {
    await api.delete(
      `/months/${month.value}/trainees/${traineeId}/assignments/${date}`
    );

    await fetchData();
  } catch (e) {
    console.error('Error clearing assignment:', e);
    if (e.response?.status !== 404) {
      alert('Erro ao limpar escalação');
    }
  } finally {
    // Clear loading state
    loadingCell.value = null;
  }
};

onMounted(fetchData);
</script>
