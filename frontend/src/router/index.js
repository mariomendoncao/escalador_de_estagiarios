import { createRouter, createWebHistory } from 'vue-router';
import MonthSelection from '../views/MonthSelection.vue';
import Import from '../views/Import.vue';
import Trainees from '../views/Trainees.vue';
import Availability from '../views/Availability.vue';
import Schedule from '../views/Schedule.vue';

const routes = [
    { path: '/', component: MonthSelection },
    { path: '/import', component: Import },
    { path: '/trainees', component: Trainees },
    { path: '/availability', component: Availability },
    { path: '/schedule', component: Schedule },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
