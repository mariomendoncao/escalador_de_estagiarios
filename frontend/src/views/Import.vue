<template>
  <div class="space-y-6">
    <div class="bg-indigo-600 shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-white">Working on: {{ formatMonth(selectedMonth) }}</h2>
          <p class="text-indigo-200 text-sm mt-1">Import data for this month</p>
        </div>
        <button
          @click="changeMonth"
          class="inline-flex items-center px-4 py-2 border border-white text-sm font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50"
        >
          Change Month
        </button>
      </div>
    </div>

    <!-- Import Trainees List -->
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="md:grid md:grid-cols-3 md:gap-6">
        <div class="md:col-span-1">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Import Trainees</h3>
          <p class="mt-1 text-sm text-gray-500">
            Paste a JSON array with trainee names.
          </p>
          <div class="mt-3 text-xs text-gray-600 bg-gray-50 p-3 rounded font-mono">
            <pre>[
  "1S SOLANGE",
  "3S ANDRADE",
  "3S MURILO"
]</pre>
          </div>
        </div>
        <div class="mt-5 md:mt-0 md:col-span-2">
          <form @submit.prevent="importTraineeList">
            <div class="space-y-4">
              <div>
                <label for="traineeListJson" class="block text-sm font-medium text-gray-700">JSON Array</label>
                <textarea
                  id="traineeListJson"
                  v-model="traineeListJson"
                  rows="12"
                  class="mt-1 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md font-mono"
                  placeholder='["1S SOLANGE", "3S ANDRADE", ...]'
                ></textarea>
              </div>
              <div class="flex justify-end">
                <button
                  type="submit"
                  class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Import Trainees
                </button>
              </div>
            </div>
          </form>
          <div v-if="traineeListMessage" class="mt-4 p-3 rounded" :class="traineeListMessageClass">
            {{ traineeListMessage }}
          </div>
        </div>
      </div>
    </div>

    <!-- Import Unavailability -->
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="md:grid md:grid-cols-3 md:gap-6">
        <div class="md:col-span-1">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Import Unavailability</h3>
          <p class="mt-1 text-sm text-gray-500">
            Paste the raw text containing trainee unavailability. Format: Nome: ... Início: ... Fim: ... Descrição: ...
          </p>
        </div>
        <div class="mt-5 md:mt-0 md:col-span-2">
          <form @submit.prevent="importUnavailability">
            <div class="space-y-4">
              <div>
                <label for="unavailabilityText" class="block text-sm font-medium text-gray-700">Raw Text</label>
                <textarea
                  id="unavailabilityText"
                  v-model="unavailabilityText"
                  rows="10"
                  class="mt-1 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md font-mono"
                  placeholder="Paste unavailability text here..."
                ></textarea>
              </div>
              <div class="flex justify-end">
                <button
                  type="submit"
                  class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Import Unavailability
                </button>
              </div>
            </div>
          </form>
          <div v-if="unavailabilityMessage" class="mt-4 p-3 rounded" :class="unavailabilityMessageClass">
            {{ unavailabilityMessage }}
          </div>
        </div>
      </div>
    </div>

    <!-- Import Férias (Vacations) -->
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="md:grid md:grid-cols-3 md:gap-6">
        <div class="md:col-span-1">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Import Férias (Vacations)</h3>
          <p class="mt-1 text-sm text-gray-500">
            Paste the vacation schedule text. Format: Entry number, Nome, Início, Fim, Quantidade de dias de férias...
          </p>
          <div class="mt-3 text-xs text-gray-600 bg-gray-50 p-3 rounded font-mono">
            <pre>Fériasfe
1
Nome: 3S SADE
Início: 23/11/2025 00:00
Fim: 07/12/2025 00:00
...</pre>
          </div>
        </div>
        <div class="mt-5 md:mt-0 md:col-span-2">
          <form @submit.prevent="importVacations">
            <div class="space-y-4">
              <div>
                <label for="vacationText" class="block text-sm font-medium text-gray-700">Vacation Text</label>
                <textarea
                  id="vacationText"
                  v-model="vacationText"
                  rows="10"
                  class="mt-1 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md font-mono"
                  placeholder="Paste vacation schedule here..."
                ></textarea>
              </div>
              <div class="flex justify-end">
                <button
                  type="submit"
                  class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Import Vacations
                </button>
              </div>
            </div>
          </form>
          <div v-if="vacationMessage" class="mt-4 p-3 rounded" :class="vacationMessageClass">
            {{ vacationMessage }}
          </div>
        </div>
      </div>
    </div>

    <!-- Import Instructor Capacity -->
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="md:grid md:grid-cols-3 md:gap-6">
        <div class="md:col-span-1">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Import Instructor Capacity</h3>
          <p class="mt-1 text-sm text-gray-500">
            Paste the JSON array with instructor capacity data. Format: [{"data": "YYYY-MM-DD", "soma_total": [{"turno": 1, "total": 2}, ...]}]
          </p>
        </div>
        <div class="mt-5 md:mt-0 md:col-span-2">
          <form @submit.prevent="importCapacity">
            <div class="space-y-4">
              <div>
                <label for="capacityJson" class="block text-sm font-medium text-gray-700">JSON Data</label>
                <textarea
                  id="capacityJson"
                  v-model="capacityJson"
                  rows="10"
                  class="mt-1 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md font-mono text-xs"
                  placeholder='[{"data": "2025-11-01", "soma_total": [{"turno": 1, "total": 2}, {"turno": 2, "total": 1}]}]'
                ></textarea>
              </div>
              <div class="flex justify-end">
                <button
                  type="submit"
                  class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  Import Capacity
                </button>
              </div>
            </div>
          </form>
          <div v-if="capacityMessage" class="mt-4 p-3 rounded" :class="capacityMessageClass">
            {{ capacityMessage }}
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-lg font-medium text-gray-900">Next Steps</h3>
          <p class="text-sm text-gray-500 mt-1">After importing data, you can view trainees or generate the schedule.</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="goToTrainees"
            class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            View Trainees
          </button>
          <button
            @click="goToSchedule"
            class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Go to Schedule
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { useMonth } from '../composables/useMonth';

const router = useRouter();
const { month: selectedMonth, isValidMonth } = useMonth();
const traineeListJson = ref('');
const traineeListMessage = ref('');
const unavailabilityText = ref('');
const unavailabilityMessage = ref('');
const vacationText = ref('');
const vacationMessage = ref('');
const capacityJson = ref('');
const capacityMessage = ref('');

const traineeListMessageClass = computed(() => {
  return traineeListMessage.value.includes('Error') || traineeListMessage.value.includes('error')
    ? 'bg-red-100 text-red-800'
    : 'bg-green-100 text-green-800';
});

const unavailabilityMessageClass = computed(() => {
  return unavailabilityMessage.value.includes('Error') || unavailabilityMessage.value.includes('error')
    ? 'bg-red-100 text-red-800'
    : 'bg-green-100 text-green-800';
});

const vacationMessageClass = computed(() => {
  return vacationMessage.value.includes('Error') || vacationMessage.value.includes('error')
    ? 'bg-red-100 text-red-800'
    : 'bg-green-100 text-green-800';
});

const capacityMessageClass = computed(() => {
  return capacityMessage.value.includes('Error') || capacityMessage.value.includes('error')
    ? 'bg-red-100 text-red-800'
    : 'bg-green-100 text-green-800';
});

const formatMonth = (monthStr) => {
  if (!monthStr) return 'No month selected';
  const [year, month] = monthStr.split('-');
  const date = new Date(year, month - 1, 1);
  return date.toLocaleString('pt-BR', { month: 'long', year: 'numeric' }).toUpperCase();
};

const changeMonth = () => {
  router.push('/');
};

const importTraineeList = async () => {
  if (!traineeListJson.value) {
    traineeListMessage.value = 'Please paste JSON data';
    return;
  }

  try {
    const names = JSON.parse(traineeListJson.value);
    if (!Array.isArray(names)) {
      traineeListMessage.value = 'Invalid format. Must be a JSON array of strings.';
      return;
    }

    const response = await api.post(`/months/${selectedMonth.value}/trainees/import-list`, names);
    traineeListMessage.value = `Success! Imported ${response.data.imported} trainees.`;
    traineeListJson.value = '';
  } catch (e) {
    console.error('Error importing trainee list:', e);
    if (e.response && e.response.status === 404) {
      traineeListMessage.value = 'Selected month no longer exists. Please select another month.';
      setTimeout(() => router.push('/'), 2000);
    } else if (e instanceof SyntaxError) {
      traineeListMessage.value = 'Error parsing JSON. Please check the format.';
    } else {
      traineeListMessage.value = 'Error importing trainees. Please check the JSON format.';
    }
  }
};

const importUnavailability = async () => {
  if (!unavailabilityText.value) {
    unavailabilityMessage.value = 'Please paste unavailability text';
    return;
  }

  try {
    const response = await api.post(
      `/months/${selectedMonth.value}/trainees/import-text`,
      unavailabilityText.value,
      { headers: { 'Content-Type': 'text/plain' } }
    );

    unavailabilityMessage.value = `Success! Imported ${response.data.imported_entries} entries for ${response.data.trainees_affected.length} trainees.`;
    unavailabilityText.value = '';
  } catch (e) {
    console.error('Error importing unavailability:', e);
    if (e.response && e.response.status === 404) {
      unavailabilityMessage.value = 'Selected month no longer exists. Please select another month.';
      setTimeout(() => router.push('/'), 2000);
    } else {
      unavailabilityMessage.value = 'Error importing unavailability. Check console for details.';
    }
  }
};

const preprocessVacationText = (text) => {
  // Remove header line if present
  let cleaned = text.replace(/^Fériasfe\s*/i, '');

  // Remove entry numbers (standalone numbers before "Nome:")
  cleaned = cleaned.replace(/^\d+\s*$/gm, '');

  const entries = [];
  const lines = cleaned.split('\n');
  let currentEntry = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    if (line.startsWith('Nome:')) {
      // Start of new entry, save previous if exists
      if (currentEntry.length > 0) {
        entries.push(currentEntry.join('\n'));
      }
      currentEntry = [line];
    } else if (line.startsWith('Função:')) {
      currentEntry.push(line);
    } else if (line.startsWith('Início:')) {
      currentEntry.push(line);
    } else if (line.startsWith('Fim:')) {
      currentEntry.push(line);
      // Add Descrição after Fim
      currentEntry.push('Descrição: Férias');
    } else if (line.startsWith('Quantidade de dias de férias')) {
      // Skip these lines - we already added "Descrição: Férias"
      continue;
    }
  }

  // Don't forget last entry
  if (currentEntry.length > 0) {
    entries.push(currentEntry.join('\n'));
  }

  return entries.join('\n\n');
};

const importVacations = async () => {
  if (!vacationText.value) {
    vacationMessage.value = 'Please paste vacation text';
    return;
  }

  try {
    // Preprocess the vacation format to standard unavailability format
    const processedText = preprocessVacationText(vacationText.value);

    // Call the same endpoint as unavailability
    const response = await api.post(
      `/months/${selectedMonth.value}/trainees/import-text`,
      processedText,
      { headers: { 'Content-Type': 'text/plain' } }
    );

    vacationMessage.value = `Success! Imported ${response.data.imported_entries} vacation entries for ${response.data.trainees_affected.length} trainees.`;
    vacationText.value = '';
  } catch (e) {
    console.error('Error importing vacations:', e);
    if (e.response && e.response.status === 404) {
      vacationMessage.value = 'Selected month no longer exists. Please select another month.';
      setTimeout(() => router.push('/'), 2000);
    } else {
      vacationMessage.value = 'Error importing vacations. Check console for details.';
    }
  }
};

const importCapacity = async () => {
  if (!capacityJson.value) {
    capacityMessage.value = 'Please paste JSON data';
    return;
  }

  try {
    const data = JSON.parse(capacityJson.value);
    const response = await api.post(`/months/${selectedMonth.value}/instructor-capacity/import-json`, data);
    capacityMessage.value = response.data.message || `Success! Imported capacity data.`;
    capacityJson.value = '';
  } catch (e) {
    console.error('Error importing capacity:', e);
    if (e.response && e.response.status === 404) {
      capacityMessage.value = 'Selected month no longer exists. Please select another month.';
      setTimeout(() => router.push('/'), 2000);
    } else if (e.response && e.response.status === 400) {
      capacityMessage.value = e.response.data.detail || 'Error importing capacity. Please check the JSON format.';
    } else {
      capacityMessage.value = 'Error importing capacity. Please check the JSON format.';
    }
  }
};

const goToTrainees = () => {
  router.push(`/trainees/${selectedMonth.value}`);
};

const goToSchedule = () => {
  router.push(`/schedule/${selectedMonth.value}`);
};

onMounted(() => {
  if (!isValidMonth.value) {
    alert('Invalid or missing month. Please select a month.');
    router.push('/');
  }
});
</script>
