<template>
  <div class="space-y-6">
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="md:grid md:grid-cols-3 md:gap-6">
        <div class="md:col-span-1">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Import Capacity</h3>
          <p class="mt-1 text-sm text-gray-500">
            Paste the HTML table content here to import instructor capacity.
          </p>
        </div>
        <div class="mt-5 md:mt-0 md:col-span-2">
          <form @submit.prevent="importCapacity">
            <div class="grid grid-cols-6 gap-6">
              <div class="col-span-6 sm:col-span-3">
                <label for="month" class="block text-sm font-medium text-gray-700">Month</label>
                <input type="month" name="month" id="month" v-model="month" class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
              </div>

              <div class="col-span-6">
                <label for="html_content" class="block text-sm font-medium text-gray-700">HTML Content</label>
                <div class="mt-1">
                  <textarea id="html_content" name="html_content" rows="10" v-model="htmlContent" class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border border-gray-300 rounded-md" placeholder="Paste HTML here..."></textarea>
                </div>
              </div>
            </div>
            <div class="mt-4 flex justify-end">
              <button type="submit" class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                Import
              </button>
            </div>
          </form>
          <div v-if="message" class="mt-4 text-sm text-green-600">
            {{ message }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';

const month = ref(new Date().toISOString().slice(0, 7));
const htmlContent = ref('');
const message = ref('');

const importCapacity = async () => {
  try {
    const response = await api.post(`/instructor-capacity/import-with-month?month=${month.value}`, htmlContent.value, {
      headers: {
        'Content-Type': 'text/plain'
      }
    });
    message.value = response.data.message;
    htmlContent.value = '';
  } catch (error) {
    console.error(error);
    message.value = 'Error importing capacity.';
  }
};
</script>
