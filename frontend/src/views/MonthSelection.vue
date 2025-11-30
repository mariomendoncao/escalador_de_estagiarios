<template>
  <div class="space-y-6">
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-4">Select a Month to Work On</h2>
      <p class="text-sm text-gray-600 mb-6">
        Choose an existing month or create a new one. Each month has its own set of trainees, availability, and schedules.
      </p>

      <div class="mb-6">
        <h3 class="text-lg font-medium text-gray-900 mb-3">Create New Month</h3>
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <label for="newMonth" class="block text-sm font-medium text-gray-700">Month</label>
            <input
              type="month"
              id="newMonth"
              v-model="newMonth"
              class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
            >
          </div>
          <button
            @click="createMonth"
            class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Create Month
          </button>
        </div>
      </div>

      <div>
        <h3 class="text-lg font-medium text-gray-900 mb-3">Existing Months</h3>
        <div v-if="months.length === 0" class="text-gray-500 text-sm">
          No months created yet. Create one above to get started.
        </div>
        <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="month in months"
            :key="month.id"
            class="border border-gray-300 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            @click="selectMonth(month.month)"
          >
            <div class="flex justify-between items-start">
              <div>
                <h4 class="text-lg font-semibold text-gray-900">
                  {{ formatMonth(month.month) }}
                </h4>
                <p class="text-sm text-gray-500">
                  Created: {{ formatDate(month.created_at) }}
                </p>
              </div>
              <button
                @click.stop="deleteMonth(month.month)"
                class="text-red-600 hover:text-red-800 text-sm"
              >
                Delete
              </button>
            </div>
            <button
              @click.stop="selectMonth(month.month)"
              class="mt-3 w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Work on this Month
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const months = ref([]);
const newMonth = ref(new Date().toISOString().slice(0, 7));

const fetchMonths = async () => {
  try {
    const response = await api.get('/months');
    months.value = response.data;
  } catch (e) {
    console.error('Error fetching months:', e);
  }
};

const createMonth = async () => {
  if (!newMonth.value) {
    alert('Please select a month');
    return;
  }

  try {
    await api.post('/months', { month: newMonth.value });
    await fetchMonths();
    alert(`Month ${newMonth.value} created successfully!`);
  } catch (e) {
    console.error('Error creating month:', e);
    alert('Error creating month. It may already exist.');
  }
};

const selectMonth = (month) => {
  // Redirect to import page with month in URL
  router.push(`/import/${month}`);
};

const deleteMonth = async (month) => {
  if (!confirm(`Delete all data for ${month}? This cannot be undone.`)) {
    return;
  }

  try {
    await api.delete(`/months/${month}`);

    await fetchMonths();
    alert(`Month ${month} deleted successfully`);
  } catch (e) {
    console.error('Error deleting month:', e);
    alert('Error deleting month');
  }
};

const formatMonth = (monthStr) => {
  const [year, month] = monthStr.split('-');
  const date = new Date(year, month - 1, 1);
  return date.toLocaleString('pt-BR', { month: 'long', year: 'numeric' }).toUpperCase();
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('pt-BR');
};

onMounted(fetchMonths);
</script>
