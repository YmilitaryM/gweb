export default defineNuxtRouteMiddleware(() => {
  if (import.meta.client) {
    const token = localStorage.getItem('admin_token');
    if (!token) {
      return navigateTo('/admin/login');
    }
  }
});
