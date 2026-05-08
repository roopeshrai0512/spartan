// Spartan Gym - shared JS
document.addEventListener("DOMContentLoaded", () => {
  // Activate sidebar/nav links by current path
  const here = window.location.pathname;
  document.querySelectorAll(".dash-sidebar a, .navbar-nav .nav-link").forEach((a) => {
    if (a.getAttribute("href") === here) a.classList.add("active");
  });

  // Animate stat counters
  document.querySelectorAll(".stat-value[data-count]").forEach((el) => {
    const target = parseInt(el.dataset.count, 10) || 0;
    let cur = 0;
    const step = Math.max(1, Math.floor(target / 40));
    const tick = () => {
      cur += step;
      if (cur >= target) { el.textContent = target; return; }
      el.textContent = cur;
      requestAnimationFrame(tick);
    };
    tick();
  });

  // Auto-dismiss success alerts after 5s
  setTimeout(() => {
    document.querySelectorAll(".alert-success.alert-dismissible").forEach((a) => {
      const inst = bootstrap.Alert.getOrCreateInstance(a);
      inst.close();
    });
  }, 5000);
});
