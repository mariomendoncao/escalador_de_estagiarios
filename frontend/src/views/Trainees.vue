<template>
  <div class="space-y-6">
    <div class="bg-indigo-600 shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold text-white">Trainees for: {{ formatMonth(selectedMonth) }}</h2>
          <p class="text-indigo-200 text-sm mt-1">Manage trainees for this month</p>
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
          <h3 class="text-lg font-medium leading-6 text-gray-900">Add Trainee</h3>
          <p class="mt-1 text-sm text-gray-500">
            Add a single trainee to this month.
          </p>
        </div>
        <div class="mt-5 md:mt-0 md:col-span-2">
          <form @submit.prevent="addTrainee" class="flex gap-4">
            <input
              type="text"
              v-model="newTraineeName"
              placeholder="Trainee Name"
              class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
            >
            <button
              type="submit"
              class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Add
            </button>
          </form>
        </div>
      </div>
    </div>

    <div class="flex flex-col">
      <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
          <div class="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" class="relative px-6 py-3">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="trainee in trainees" :key="trainee.id">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {{ trainee.name }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span
                      :class="trainee.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                      class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                    >
                      {{ trainee.active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      @click="toggleActive(trainee)"
                      class="text-indigo-600 hover:text-indigo-900 mr-4"
                    >
                      {{ trainee.active ? 'Deactivate' : 'Activate' }}
                    </button>
                    <button
                      @click="deleteTrainee(trainee.id)"
                      class="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
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
const selectedMonth = ref(localStorage.getItem('selectedMonth') || '');
const trainees = ref([]);
const newTraineeName = ref('');

const formatMonth = (monthStr) => {
  if (!monthStr) return 'No month selected';
  const [year, month] = monthStr.split('-');
  const date = new Date(year, month - 1, 1);
  return date.toLocaleString('pt-BR', { month: 'long', year: 'numeric' }).toUpperCase();
};

const changeMonth = () => {
  router.push('/');
};

const fetchTrainees = async () => {
  if (!selectedMonth.value) {
    alert('No month selected');
    router.push('/');
    return;
  }

  try {
    const response = await api.get(`/months/${selectedMonth.value}/trainees`);
    trainees.value = response.data;
  } catch (e) {
    console.error('Error fetching trainees:', e);
    if (e.response && e.response.status === 404) {
      alert('Selected month no longer exists. Please select another month.');
      localStorage.removeItem('selectedMonth');
      router.push('/');
    }
  }
};

const addTrainee = async () => {
  if (!newTraineeName.value) return;

  try {
    await api.post(`/months/${selectedMonth.value}/trainees`, {
      name: newTraineeName.value,
      active: true
    });
    newTraineeName.value = '';
    fetchTrainees();
  } catch (e) {
    console.error('Error adding trainee:', e);
    alert('Error adding trainee');
  }
};

const toggleActive = async (trainee) => {
  try {
    await api.put(`/months/${selectedMonth.value}/trainees/${trainee.id}`, {
      name: trainee.name,
      active: !trainee.active
    });
    fetchTrainees();
  } catch (e) {
    console.error('Error toggling trainee:', e);
  }
};

const deleteTrainee = async (id) => {
  if (confirm('Are you sure?')) {
    try {
      await api.delete(`/months/${selectedMonth.value}/trainees/${id}`);
      fetchTrainees();
    } catch (e) {
      console.error('Error deleting trainee:', e);
    }
  }
};

onMounted(fetchTrainees);
</script>
