import { createRouter, createWebHistory } from 'vue-router';
import MonthSelection from '../views/MonthSelection.vue';
import Import from '../views/Import.vue';
import Trainees from '../views/Trainees.vue';
import Availability from '../views/Availability.vue';
import Schedule from '../views/Schedule.vue';

// Guard para validar formato do mês (YYYY-MM)
const validateMonthFormat = (to, from, next) => {
    const month = to.params.month;

    if (!month || !/^\d{4}-\d{2}$/.test(month)) {
        next('/');  // Redireciona para seleção se inválido
    } else {
        next();
    }
};

const routes = [
    { path: '/', component: MonthSelection },
    { path: '/import/:month', component: Import, beforeEnter: validateMonthFormat },
    { path: '/trainees/:month', component: Trainees, beforeEnter: validateMonthFormat },
    { path: '/availability/:month', component: Availability, beforeEnter: validateMonthFormat },
    { path: '/schedule/:month', component: Schedule, beforeEnter: validateMonthFormat },
    // Catch-all routes: redirect to month selection if no month parameter
    { path: '/import', redirect: '/' },
    { path: '/trainees', redirect: '/' },
    { path: '/availability', redirect: '/' },
    { path: '/schedule', redirect: '/' },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
