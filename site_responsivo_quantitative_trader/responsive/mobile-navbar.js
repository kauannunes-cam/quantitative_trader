class MobileNavbar {
  constructor(mobileMenu, navList, navLinks) {
    this.mobileMenu = document.querySelector(mobileMenu);
    this.navList = document.querySelector(navList);
    this.navLinks = document.querySelectorAll(navLinks);
    this.activeClass = "active";
    this.handleClick = this.handleClick.bind(this);
  }

  animateLinks() {
    this.navLinks.forEach((link, index) => {
      link.style.animation
        ? (link.style.animation = "")
        : (link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7 + 0.3}s`);
    });
  }

  handleClick() {
    this.navList.classList.toggle(this.activeClass);
    this.mobileMenu.classList.toggle(this.activeClass);
    this.animateLinks();
  }

  addClickEvent() {
    this.mobileMenu.addEventListener("click", this.handleClick);
  }

  init() {
    if (this.mobileMenu) {
      this.addClickEvent();
    }
    return this;
  }
}

const mobileNavbar = new MobileNavbar(".mobile-menu", ".nav-list", ".nav-list li");
mobileNavbar.init();

document.getElementById('link-quem-somos-nos').addEventListener('click', function() {
  document.getElementById('quem-somos-nos').classList.remove('hidden');
  document.getElementById('analise-quantitativa').classList.add('hidden');
});

document.getElementById('link-analise-quantitativa').addEventListener('click', function() {
  var container = document.getElementById('graficos-container');
  container.style.display = container.style.display === 'none' ? 'block' : 'none';
  if (container.style.display === 'block') {
    mostrarGrafico('fig1.html');
  }
});

function mostrarGrafico(src) {
  document.getElementById('grafico').src = src;
}
