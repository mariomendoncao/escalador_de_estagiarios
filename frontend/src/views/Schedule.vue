<template>
  <div class="space-y-6">
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="flex justify-between items-center">
        <div class="flex items-center space-x-4">
          <label for="month" class="block text-sm font-medium text-gray-700">Mês</label>
          <input type="month" id="month" v-model="month" @change="fetchData" class="focus:ring-indigo-500 focus:border-indigo-500 block shadow-sm sm:text-sm border-gray-300 rounded-md">
        </div>
        <div class="flex space-x-4">
          <button @click="generateSchedule" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Gerar Escala
          </button>
          <button @click="clearSchedule" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
            Limpar Escala
          </button>
          <button @click="exportCSV" class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Exportar CSV
          </button>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          @click="currentTab = 'schedule'"
          :class="[
            currentTab === 'schedule'
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Escala
        </button>
        <button
          @click="currentTab = 'parameters'"
          :class="[
            currentTab === 'parameters'
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          Parâmetros
        </button>
      </nav>
    </div>

    <!-- Schedule View -->
    <div v-if="currentTab === 'schedule'" class="space-y-6">
      <!-- Instructor Capacity Table -->
      <div class="bg-white shadow overflow-x-auto sm:rounded-lg">
        <div class="px-4 py-3 border-b border-gray-200 bg-blue-600">
          <h3 class="text-lg font-medium text-white">Capacidade de Instrutores</h3>
        </div>
        <div class="inline-block min-w-full align-middle">
          <table class="min-w-full border-collapse border border-gray-300 text-xs">
            <thead>
              <!-- Days Header -->
              <tr class="bg-blue-500 text-white">
                <th class="border border-gray-300 px-1 py-1"></th>
                <th v-for="day in days" :key="`cap-h-${day.date}`" class="border border-gray-300 px-1 py-1 text-center font-bold" :class="{'bg-green-400 text-black': isWeekend(day.date)}">
                  {{ day.day }}
                </th>
              </tr>
              <!-- Weekdays Header -->
              <tr class="bg-blue-100">
                <th class="border border-gray-300 px-1 py-1"></th>
                <th v-for="day in days" :key="`cap-w-${day.date}`" class="border border-gray-300 px-1 py-1 text-center text-[10px] uppercase" :class="{'bg-green-300': isWeekend(day.date)}">
                  {{ day.weekday }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white">
              <!-- Capacity Rows -->
              <tr class="bg-blue-50">
                <td class="border border-gray-300 px-2 py-1 font-bold text-gray-900">Manhã</td>
                <td v-for="day in days" :key="`cap-m-${day.date}`" class="border border-gray-300 px-1 py-1 text-center font-medium" :class="{'bg-green-100': isWeekend(day.date)}">
                  {{ getCapacity(day.date, 'manha') }}
                </td>
              </tr>
              <tr class="bg-blue-50">
                <td class="border border-gray-300 px-2 py-1 font-bold text-gray-900">Tarde</td>
                <td v-for="day in days" :key="`cap-t-${day.date}`" class="border border-gray-300 px-1 py-1 text-center font-medium" :class="{'bg-green-100': isWeekend(day.date)}">
                  {{ getCapacity(day.date, 'tarde') }}
                </td>
              </tr>
              <tr class="bg-blue-50">
                <td class="border border-gray-300 px-2 py-1 font-bold text-gray-900">Pernoite</td>
                <td v-for="day in days" :key="`cap-p-${day.date}`" class="border border-gray-300 px-1 py-1 text-center font-medium" :class="{'bg-green-100': isWeekend(day.date)}">
                  {{ getCapacity(day.date, 'pernoite') }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
  
      <!-- Trainee Schedule Table -->
      <div class="bg-white shadow overflow-x-auto sm:rounded-lg">
        <div class="inline-block min-w-full align-middle">
          <table class="min-w-full border-collapse border border-gray-300 text-xs">
            <thead>
              <!-- Summary Rows -->
              <tr class="bg-red-100">
                <th class="border border-gray-300 px-1 py-1 text-left font-medium text-gray-900 w-48">Manhã</th>
                <th v-for="day in days" :key="`m-${day.date}`" class="border border-gray-300 px-1 py-1 text-center font-medium text-gray-900 w-8" :class="{'bg-green-100': isWeekend(day.date)}">
                  {{ getShiftCount(day.date, 'manha') }}
                </th>
              </tr>
              <tr class="bg-red-100">
                <th class="border border-gray-300 px-1 py-1 text-left font-medium text-gray-900">Tarde</th>
                <th v-for="day in days" :key="`t-${day.date}`" class="border border-gray-300 px-1 py-1 text-center font-medium text-gray-900" :class="{'bg-green-100': isWeekend(day.date)}">
                  {{ getShiftCount(day.date, 'tarde') }}
                </th>
              </tr>
              <tr class="bg-red-100">
                <th class="border border-gray-300 px-1 py-1 text-left font-medium text-gray-900">Pernoite</th>
                <th v-for="day in days" :key="`p-${day.date}`" class="border border-gray-300 px-1 py-1 text-center font-medium text-gray-900" :class="{'bg-green-100': isWeekend(day.date)}">
                  {{ getShiftCount(day.date, 'pernoite') }}
                </th>
              </tr>
              
              <!-- Header Separator -->
              <tr>
                <th :colspan="days.length + 1" class="border border-gray-300 px-1 py-1 bg-orange-600 text-white text-center font-bold uppercase tracking-wider">
                  {{ getMonthName(month) }}
                </th>
              </tr>
  
              <!-- Days Header -->
              <tr class="bg-orange-500 text-white">
                <th class="border border-gray-300 px-1 py-1"></th>
                <th v-for="day in days" :key="`h-${day.date}`" class="border border-gray-300 px-1 py-1 text-center font-bold" :class="{'bg-green-400 text-black': isWeekend(day.date)}">
                  {{ day.day }}
                </th>
                <th class="border border-gray-300 px-1 py-1 text-center font-bold">Total</th>
              </tr>
              <!-- Weekdays Header -->
              <tr class="bg-orange-100">
                <th class="border border-gray-300 px-1 py-1"></th>
                <th v-for="day in days" :key="`w-${day.date}`" class="border border-gray-300 px-1 py-1 text-center text-[10px] uppercase" :class="{'bg-green-300': isWeekend(day.date)}">
                  {{ day.weekday }}
                </th>
                <th class="border border-gray-300 px-1 py-1"></th>
              </tr>
            </thead>
            <tbody class="bg-white">
              <tr v-for="trainee in trainees" :key="trainee.id">
                <td class="border border-gray-300 px-2 py-1 font-bold text-gray-900 whitespace-nowrap flex items-center justify-between">
                  <span>{{ trainee.name }}</span>
                  <button @click="clearTraineeSchedule(trainee.id)" class="ml-2 text-red-600 hover:text-red-800 text-xs" title="Limpar escala deste estagiário">
                    ✕
                  </button>
                </td>
                <td
                  v-for="day in days"
                  :key="`${trainee.id}-${day.date}`"
                  @click="handleCellClick($event, trainee.id, day.date)"
                  class="border border-gray-300 px-1 py-1 text-center font-medium"
                  :class="getCellClass(trainee.id, day.date)"
                  :style="canEdit(trainee.id, day.date) ? 'cursor: pointer;' : 'cursor: not-allowed;'"
                >
                  <span v-if="isLoading(trainee.id, day.date)" class="inline-block animate-spin">⏳</span>
                  <span v-else :class="getShiftColor(getShift(trainee.id, day.date))">
                    {{ getCellContent(trainee.id, day.date) }}
                  </span>
                </td>
                <td class="border border-gray-300 px-1 py-1 text-center font-bold text-gray-900">
                  {{ getTraineeDayCount(trainee.id) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
  
      <!-- Inline Edit Dropdown -->
      <div
        v-if="editingCell"
        class="fixed z-50 bg-white border-2 border-indigo-500 rounded-lg shadow-xl py-1 min-w-[100px]"
        :style="{ top: dropdownPosition.top + 'px', left: dropdownPosition.left + 'px' }"
        @click.stop
      >
        <button
          v-for="option in shiftOptions"
          :key="option.value"
          @click="selectShift(option.value)"
          class="w-full px-4 py-2 text-left hover:bg-indigo-50 text-sm font-medium"
          :class="getCurrentShift() === option.value ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700'"
        >
          {{ option.label }}
        </button>
        <button
          v-if="getCurrentShift()"
          @click="clearShift"
          class="w-full px-4 py-2 text-left hover:bg-red-50 text-sm font-medium text-red-600 border-t border-gray-200"
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
  return schedule.value.filter(s => s.date === date && s.shift === shift).length;
};

const getCapacity = (date, shift) => {
  const cap = capacities.value.find(c => c.date === date && c.shift === shift);
  return cap ? cap.total_instructors : 0;
};

const isWeekend = (dateStr) => {
  const d = new Date(dateStr);
  const day = d.getDay();
  return day === 0 || day === 6; // 0 is Sunday, 6 is Saturday
};

const getMonthName = (monthStr) => {
  if (!monthStr) return '';
  const [y, m] = monthStr.split('-');
  const date = new Date(y, m - 1, 1);
  return date.toLocaleString('pt-BR', { month: 'long', year: 'numeric' }).toUpperCase();
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
  // Block if trainee is unavailable
  if (isUnavailable(traineeId, date)) {
    return;
  }

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

const selectShift = async (shift) => {
  if (!editingCell.value) return;

  const { traineeId, date } = editingCell.value;
  
  // Close dropdown immediately for instant feedback
  closeDropdown();
  
  // Set loading state
  loadingCell.value = { traineeId, date };

  try {
    await api.post(
      `/months/${month.value}/trainees/${traineeId}/assignments`,
      { date, shift }
    );

    await fetchData();
  } catch (e) {
    console.error('Error saving assignment:', e);
    if (e.response?.data?.detail) {
      alert(e.response.data.detail);
    } else {
      alert('Erro ao salvar escalação');
    }
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
