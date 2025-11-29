<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-indigo-600 shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-white">
            Indisponibilidades: {{ formatMonth(month) }}
          </h2>
          <p class="text-indigo-200 text-sm mt-1">
            Clique em um dia para adicionar/editar indisponibilidade
          </p>
        </div>
        <button
          @click="changeMonth"
          class="inline-flex items-center px-4 py-2 border border-white text-sm font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50"
        >
          Mudar Mês
        </button>
      </div>
    </div>

    <!-- Availability Table -->
    <div class="bg-white shadow overflow-x-auto sm:rounded-lg">
      <table class="min-w-full border-collapse border border-gray-300 text-xs">
        <thead>
          <!-- Days Header -->
          <tr class="bg-indigo-500 text-white">
            <th class="border border-gray-300 px-2 py-1 sticky left-0 bg-indigo-500 z-10">Estagiário</th>
            <th
              v-for="day in days"
              :key="`h-${day.date}`"
              class="border border-gray-300 px-1 py-1 text-center font-bold"
              :class="{'bg-green-400 text-black': isWeekend(day.date)}"
            >
              {{ day.day }}
            </th>
          </tr>
          <!-- Weekdays Header -->
          <tr class="bg-indigo-100">
            <th class="border border-gray-300 px-2 py-1 sticky left-0 bg-indigo-100 z-10"></th>
            <th
              v-for="day in days"
              :key="`w-${day.date}`"
              class="border border-gray-300 px-1 py-1 text-center text-[10px] uppercase"
              :class="{'bg-green-300': isWeekend(day.date)}"
            >
              {{ day.weekday }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white">
          <!-- Trainee Rows -->
          <tr v-for="trainee in trainees" :key="trainee.id">
            <td class="border border-gray-300 px-2 py-1 font-bold text-gray-900 whitespace-nowrap sticky left-0 bg-white z-10">
              {{ trainee.name }}
            </td>
            <td
              v-for="day in days"
              :key="`${trainee.id}-${day.date}`"
              @click="openModal(trainee, day.date)"
              class="border border-gray-300 px-1 py-1 text-center cursor-pointer hover:bg-blue-50 text-[10px]"
              :class="getCellClass(trainee.id, day.date)"
            >
              {{ getUnavailabilityReason(trainee.id, day.date) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-bold mb-4 text-gray-900">
          Indisponibilidade: {{ selectedTrainee?.name }}
        </h3>
        <p class="text-sm text-gray-600 mb-4">
          Data: {{ formatDate(selectedDate) }}
        </p>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Motivo da Indisponibilidade
          </label>
          <input
            ref="reasonInput"
            v-model="editReason"
            type="text"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Ex: Comissão QSCON, RISAER, Férias..."
            @keyup.enter="saveUnavailability"
            @keyup.esc="closeModal"
          />
          <p class="text-xs text-gray-500 mt-1">
            Deixe em branco para remover a indisponibilidade
          </p>
        </div>

        <div class="flex justify-end space-x-3">
          <button
            @click="closeModal"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            v-if="hasExistingUnavailability"
            @click="deleteUnavailability"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Remover
          </button>
          <button
            @click="saveUnavailability"
            class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Salvar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const month = ref(localStorage.getItem('selectedMonth') || '');
const trainees = ref([]);
const availabilities = ref([]);
const showModal = ref(false);
const selectedTrainee = ref(null);
const selectedDate = ref(null);
const editReason = ref('');
const reasonInput = ref(null);

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

const hasExistingUnavailability = computed(() => {
  if (!selectedTrainee.value || !selectedDate.value) return false;
  return availabilities.value.some(a =>
    a.trainee_id === selectedTrainee.value.id &&
    a.date === selectedDate.value &&
    !a.available
  );
});

const formatMonth = (monthStr) => {
  if (!monthStr) return '';
  const [year, month] = monthStr.split('-');
  const date = new Date(year, month - 1, 1);
  return date.toLocaleString('pt-BR', { month: 'long', year: 'numeric' }).toUpperCase();
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR');
};

const isWeekend = (dateStr) => {
  const d = new Date(dateStr);
  const day = d.getDay();
  return day === 0 || day === 6;
};

const changeMonth = () => {
  router.push('/');
};

const fetchData = async () => {
  if (!month.value) {
    alert('Nenhum mês selecionado');
    router.push('/');
    return;
  }

  try {
    const [traineesRes, availabilitiesRes] = await Promise.all([
      api.get(`/months/${month.value}/trainees`),
      api.get(`/months/${month.value}/availability`)
    ]);

    trainees.value = traineesRes.data.filter(t => t.active);
    availabilities.value = availabilitiesRes.data;
  } catch (e) {
    console.error('Error fetching data:', e);
    if (e.response && e.response.status === 404) {
      alert('Mês selecionado não existe mais. Selecione outro mês.');
      localStorage.removeItem('selectedMonth');
      router.push('/');
    }
  }
};

const getUnavailabilityReason = (traineeId, date) => {
  // Find ANY unavailable record for this trainee on this date
  // (all 3 shifts should have same reason since we mark all together)
  const unavail = availabilities.value.find(a =>
    a.trainee_id === traineeId &&
    a.date === date &&
    !a.available
  );

  return unavail ? (unavail.reason || '') : '';
};

const getCellClass = (traineeId, date) => {
  const classes = [];

  if (isWeekend(date)) {
    classes.push('bg-green-100');
  }

  const reason = getUnavailabilityReason(traineeId, date);
  if (reason) {
    classes.push('bg-red-200 font-medium');
  }

  return classes.join(' ');
};

const openModal = (trainee, date) => {
  selectedTrainee.value = trainee;
  selectedDate.value = date;

  // Load existing reason if available
  const existing = availabilities.value.find(a =>
    a.trainee_id === trainee.id &&
    a.date === date &&
    !a.available
  );

  editReason.value = existing?.reason || '';
  showModal.value = true;

  // Focus input after modal opens
  nextTick(() => {
    if (reasonInput.value) {
      reasonInput.value.focus();
    }
  });
};

const closeModal = () => {
  showModal.value = false;
  selectedTrainee.value = null;
  selectedDate.value = null;
  editReason.value = '';
};

const saveUnavailability = async () => {
  if (!selectedTrainee.value || !selectedDate.value) return;

  const reason = editReason.value.trim();

  // If reason is empty, delete the unavailability
  if (!reason) {
    await deleteUnavailability();
    return;
  }

  try {
    // Create/update unavailability for ALL 3 shifts
    const availabilityUpdates = [
      { date: selectedDate.value, shift: 'manha', available: false, reason },
      { date: selectedDate.value, shift: 'tarde', available: false, reason },
      { date: selectedDate.value, shift: 'pernoite', available: false, reason }
    ];

    await api.post(
      `/months/${month.value}/trainees/${selectedTrainee.value.id}/availability/bulk`,
      { availabilities: availabilityUpdates }
    );

    // Refresh data
    await fetchData();
    closeModal();
  } catch (e) {
    console.error('Error saving:', e);
    alert('Erro ao salvar indisponibilidade');
  }
};

const deleteUnavailability = async () => {
  if (!selectedTrainee.value || !selectedDate.value) return;

  try {
    // Mark ALL 3 shifts as available (removes unavailability)
    const availabilityUpdates = [
      { date: selectedDate.value, shift: 'manha', available: true, reason: null },
      { date: selectedDate.value, shift: 'tarde', available: true, reason: null },
      { date: selectedDate.value, shift: 'pernoite', available: true, reason: null }
    ];

    await api.post(
      `/months/${month.value}/trainees/${selectedTrainee.value.id}/availability/bulk`,
      { availabilities: availabilityUpdates }
    );

    // Refresh data
    await fetchData();
    closeModal();
  } catch (e) {
    console.error('Error deleting:', e);
    alert('Erro ao remover indisponibilidade');
  }
};

onMounted(fetchData);
</script>
