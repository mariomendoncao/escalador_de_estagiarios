<template>
  <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
    <div class="md:grid md:grid-cols-3 md:gap-6">
      <div class="md:col-span-1">
        <h3 class="text-lg font-medium leading-6 text-gray-900">Parâmetros da Escala</h3>
        <p class="mt-1 text-sm text-gray-500">
          Defina as regras que serão utilizadas para a geração automática da escala deste mês.
        </p>
      </div>
      <div class="mt-5 md:mt-0 md:col-span-2">
        <form @submit.prevent="saveParameters">
          <div class="grid grid-cols-6 gap-6">
            
            <div class="col-span-6 sm:col-span-3">
              <label for="total_shifts" class="block text-sm font-medium text-gray-700">Total de Plantões</label>
              <input type="number" name="total_shifts" id="total_shifts" v-model.number="params.params_total_shifts" class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
              <p class="mt-1 text-xs text-gray-500">Meta de plantões por estagiário (ex: 18)</p>
            </div>

            <div class="col-span-6 sm:col-span-3">
              <label for="night_shifts" class="block text-sm font-medium text-gray-700">Plantões Noturnos</label>
              <input type="number" name="night_shifts" id="night_shifts" v-model.number="params.params_night_shifts" class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
              <p class="mt-1 text-xs text-gray-500">Meta de plantões noturnos (ex: 2)</p>
            </div>

            <div class="col-span-6 sm:col-span-3">
              <label for="max_consecutive_work" class="block text-sm font-medium text-gray-700">Máx. Dias Trabalhados</label>
              <input type="number" name="max_consecutive_work" id="max_consecutive_work" v-model.number="params.params_max_consecutive_work_days" class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
              <p class="mt-1 text-xs text-gray-500">Limite de dias seguidos trabalhando (ex: 6)</p>
            </div>

            <div class="col-span-6 sm:col-span-3">
              <label for="max_consecutive_off" class="block text-sm font-medium text-gray-700">Máx. Dias de Folga</label>
              <input type="number" name="max_consecutive_off" id="max_consecutive_off" v-model.number="params.params_max_consecutive_days_off" class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
              <p class="mt-1 text-xs text-gray-500">Limite de dias seguidos de folga (ex: 3)</p>
            </div>

            <div class="col-span-6 sm:col-span-3">
              <label for="unavailability_weight" class="block text-sm font-medium text-gray-700">Peso da Indisponibilidade</label>
              <input type="number" name="unavailability_weight" id="unavailability_weight" v-model.number="params.params_unavailability_weight" class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
              <p class="mt-1 text-xs text-gray-500">Quanto conta cada indisponibilidade na contagem total (ex: 1)</p>
            </div>

            <div class="col-span-6">
              <div class="flex items-start">
                <div class="flex items-center h-5">
                  <input id="post_night_off" name="post_night_off" type="checkbox" v-model="params.params_post_night_shift_off" class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded">
                </div>
                <div class="ml-3 text-sm">
                  <label for="post_night_off" class="font-medium text-gray-700">Folga Pós-Pernoite</label>
                  <p class="text-gray-500">Estagiário não pode ser escalado no dia seguinte ao pernoite.</p>
                </div>
              </div>
            </div>

          </div>
          
          <div class="mt-6 flex justify-end">
            <button type="submit" class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              Salvar Parâmetros
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import api from '../api';

const props = defineProps({
  month: {
    type: String,
    required: true
  }
});

const params = ref({
  params_total_shifts: 18,
  params_night_shifts: 2,
  params_max_consecutive_days_off: 3,
  params_max_consecutive_work_days: 6,
  params_unavailability_weight: 1,
  params_post_night_shift_off: true
});

const fetchParameters = async () => {
  try {
    // We fetch the monthly schedule object which contains the params
    // We can reuse the endpoint that creates/gets the schedule
    const response = await api.post('/months', { month: props.month });
    const data = response.data;
    
    params.value = {
      params_total_shifts: data.params_total_shifts,
      params_night_shifts: data.params_night_shifts,
      params_max_consecutive_days_off: data.params_max_consecutive_days_off,
      params_max_consecutive_work_days: data.params_max_consecutive_work_days,
      params_unavailability_weight: data.params_unavailability_weight,
      params_post_night_shift_off: data.params_post_night_shift_off
    };
  } catch (e) {
    console.error('Error fetching parameters:', e);
  }
};

const saveParameters = async () => {
  try {
    await api.put(`/months/${props.month}/parameters`, {
      month: props.month,
      ...params.value
    });
    alert('Parâmetros salvos com sucesso!');
  } catch (e) {
    console.error('Error saving parameters:', e);
    alert('Erro ao salvar parâmetros.');
  }
};

onMounted(fetchParameters);

watch(() => props.month, fetchParameters);

</script>
