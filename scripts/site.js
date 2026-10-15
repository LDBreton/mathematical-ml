// Shared navigation and theme controls, without external dependencies.
const menu = document.querySelector('.menu');
const sidebar = document.querySelector('#sidebar');
menu.addEventListener('click', () => {
  const open = sidebar.classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && sidebar.classList.contains('open')) {
    sidebar.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
    menu.focus();
  }
});
const currentPage = location.pathname.split('/').pop() || 'index.html';
sidebar.querySelectorAll('a').forEach(link => {
  if (link.getAttribute('href') === currentPage) {
    link.setAttribute('aria-current', 'page');
    const section = link.closest('details');
    if (section) section.open = true;
  }
});
const themeButton = document.querySelector('#theme');
function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const spanish = document.documentElement.lang === 'es';
  themeButton.setAttribute('aria-label', spanish
    ? `Cambiar a modo ${theme === 'dark' ? 'claro' : 'oscuro'}`
    : `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
}
try { setTheme(localStorage.getItem('course-theme') || 'light'); } catch { setTheme('light'); }
themeButton.addEventListener('click', () => {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  setTheme(theme);
  try { localStorage.setItem('course-theme', theme); } catch { /* Storage may be disabled. */ }
});

// Keep the current section when switching languages; never redirect the default.
document.querySelectorAll('.languages a').forEach(link => {
  link.addEventListener('click', () => {
    const destination = new URL(link.href);
    destination.hash = location.hash;
    link.href = destination.href;
  });
});
