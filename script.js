// AOS animations
document.addEventListener("DOMContentLoaded", function () {
  AOS.init({ duration: 1200, once: true, offset: 80 });
});

// tsParticles
tsParticles.load("tsparticles", {
  background: { color: { value: "transparent" } },
  fullScreen: { enable: false },
  particles: {
    number: { value: 60, density: { enable: true, area: 800 } },
    color: { value: "#60a5fa" },
    shape: { type: "line" },
    opacity: { value: 0.1 },
    size: { value: { min: 1, max: 2 } },
    move: {
      enable: true,
      speed: 6,
      direction: "bottom",
      straight: true,
      outModes: { default: "out" }
    }
  },
  detectRetina: true
});

// Countdown timer
const countdown = document.getElementById("countdown");
const launchDate = new Date("2025-10-01T00:00:00Z").getTime();

function updateCountdown() {
  const now = new Date().getTime();
  const gap = launchDate - now;

  if (gap < 0) {
    countdown.textContent = "We're Live!";
    return;
  }

  const weeks = Math.floor(gap / (1000 * 60 * 60 * 24 * 7));
  const days = Math.floor((gap % (1000 * 60 * 60 * 24 * 7)) / (1000 * 60 * 60 * 24));
  const hours = Math.floor((gap % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((gap % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((gap % (1000 * 60)) / 1000);

  countdown.innerHTML = `${weeks}w ${days}d ${hours}h ${minutes}m ${seconds}s`;
}

setInterval(updateCountdown, 1000);
updateCountdown();
