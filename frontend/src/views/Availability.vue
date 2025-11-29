<template>
  <div class="space-y-6">
    <div class="bg-indigo-600 shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-white">Availability for: {{ formatMonth(month) }}</h2>
          <p class="text-indigo-200 text-sm mt-1">Manage trainee availability for this month</p>
        </div>
        <button
          @click="changeMonth"
          class="inline-flex items-center px-4 py-2 border border-white text-sm font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50"
        >
          Change Month
        </button>
      </div>
    </div>

    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="md:grid md:grid-cols-3 md:gap-6">
        <div class="md:col-span-1">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Select Trainee</h3>
          <p class="mt-1 text-sm text-gray-500">
            Choose a trainee to edit their availability.
          </p>
        </div>
        <div class="mt-5 md:mt-0 md:col-span-2">
          <div>
            <label for="trainee" class="block text-sm font-medium text-gray-700">Trainee</label>
            <select id="trainee" v-model="selectedTraineeId" @change="fetchAvailability" class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
              <option v-for="t in trainees" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedTraineeId && days.length > 0" class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Availability Grid</h3>
        <button @click="saveAvailability" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Save Changes
        </button>
      </div>
      <div class="border-t border-gray-200 p-4">
        <div class="grid grid-cols-4 gap-4 text-center font-bold mb-2">
          <div>Day</div>
          <div>Manhã</div>
          <div>Tarde</div>
          <div>Pernoite</div>
        </div>
        <div v-for="day in days" :key="day.date" class="grid grid-cols-4 gap-4 items-center border-b py-2">
          <div class="text-sm text-gray-500">{{ day.label }}</div>
          <div v-for="shift in ['manha', 'tarde', 'pernoite']" :key="shift">
            <button 
              @click="toggle(day.date, shift)"
              :class="isAvailable(day.date, shift) ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'"
              class="w-full py-2 rounded text-sm font-medium transition-colors"
            >
              {{ isAvailable(day.date, shift) ? 'Available' : 'Unavailable' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const trainees = ref([]);
const selectedTraineeId = ref(null);
const month = ref(localStorage.getItem('selectedMonth') || new Date().toISOString().slice(0, 7));
const availabilityMap = ref({}); // key: date_shift, value: bool

const formatMonth = (monthStr) => {
  if (!monthStr) return 'No month selected';
  const [year, monthNum] = monthStr.split('-');
  const date = new Date(year, monthNum - 1, 1);
  return date.toLocaleString('pt-BR', { month: 'long', year: 'numeric' }).toUpperCase();
};

const changeMonth = () => {
  router.push('/');
};

const fetchTrainees = async () => {
  if (!month.value) {
    alert('No month selected');
    router.push('/');
    return;
  }

  try {
    const response = await api.get(`/months/${month.value}/trainees`);
    trainees.value = response.data.filter(t => t.active);
    if (trainees.value.length > 0) {
      selectedTraineeId.value = trainees.value[0].id;
      fetchAvailability();
    }
  } catch (e) {
    console.error('Error fetching trainees:', e);
    if (e.response && e.response.status === 404) {
      alert('Selected month no longer exists. Please select another month.');
      localStorage.removeItem('selectedMonth');
      router.push('/');
    }
  }
};

const days = computed(() => {
  if (!month.value) return [];
  const [y, m] = month.value.split('-').map(Number);
  const date = new Date(y, m, 0);
  const daysInMonth = date.getDate();
  const result = [];
  for (let i = 1; i <= daysInMonth; i++) {
    const d = new Date(y, m - 1, i);
    const dateStr = d.toISOString().slice(0, 10);
    result.push({
      date: dateStr,
      label: `${i} (${d.toLocaleDateString('pt-BR', { weekday: 'short' })})`
    });
  }
  return result;
});

const fetchAvailability = async () => {
  if (!selectedTraineeId.value || !month.value) return;

  availabilityMap.value = {};
  try {
    const response = await api.get(`/months/${month.value}/trainees/${selectedTraineeId.value}/availability`);
    response.data.forEach(item => {
      availabilityMap.value[`${item.date}_${item.shift}`] = item.available;
    });
  } catch (e) {
    console.error(e);
  }
};

const isAvailable = (date, shift) => {
  const key = `${date}_${shift}`;
  // If no record exists, default to true (available)
  return availabilityMap.value[key] === undefined ? true : availabilityMap.value[key];
};

const toggle = (date, shift) => {
  const key = `${date}_${shift}`;
  availabilityMap.value[key] = !availabilityMap.value[key];
};

const saveAvailability = async () => {
  const availabilities = [];
  for (const key in availabilityMap.value) {
    const [date, shift] = key.split('_');
    availabilities.push({
      date,
      shift,
      available: availabilityMap.value[key]
    });
  }

  try {
    await api.post(`/months/${month.value}/trainees/${selectedTraineeId.value}/availability/bulk`, { availabilities });
    alert('Saved!');
  } catch (e) {
    console.error('Error saving availability:', e);
    alert('Error saving availability');
  }
};

onMounted(fetchTrainees);
</script>
