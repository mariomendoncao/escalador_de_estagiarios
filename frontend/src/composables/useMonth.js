import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export function useMonth() {
  const route = useRoute();
  const router = useRouter();

  // Pega month da URL
  const month = computed(() => route.params.month);

  // Função para navegar com month
  const navigateTo = (path) => {
    if (!month.value) {
      router.push('/');
      return;
    }
    router.push(`${path}/${month.value}`);
  };

  // Verifica se month é válido (formato YYYY-MM)
  const isValidMonth = computed(() => {
    if (!month.value) return false;
    return /^\d{4}-\d{2}$/.test(month.value);
  });

  return {
    month,
    navigateTo,
    isValidMonth
  };
}
