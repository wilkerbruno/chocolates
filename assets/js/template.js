/*
    template.js — Spinassi Chocolates
    ─────────────────────────────────────────────────────────
    Carrega o template.html e injeta os três blocos compartilhados
    nas páginas que tiverem os marcadores:

        <div id="tpl-whatsapp"></div>
        <div id="tpl-menu"></div>
        <div id="tpl-rodape"></div>

    Após injetar, dispara o evento  "templateCarregado"  no window,
    para que login.js e outros scripts saibam que o DOM do menu
    já está disponível.

    Carregue este script em cada página, antes dos outros scripts:
        <script src="assets/js/template.js"></script>
*/

(function () {

    /* ── 1. Detecta o nome da página ativa ─────────────────
       Lê o atributo  data-pagina="..."  do <body>.
       Exemplos:
           <body data-pagina="home">
           <body data-pagina="produtos">
    ─────────────────────────────────────────────────────── */
    function paginaAtiva() {
        return (document.body && document.body.getAttribute('data-pagina')) || '';
    }

    /* ── 2. Marca o link ativo no menu ─────────────────────
       Todo <a data-nav="..."> dentro do menu recebe a
       classe  active  quando  data-nav === paginaAtiva().
    ─────────────────────────────────────────────────────── */
    function marcarAtivo(menuEl) {
        var pagina = paginaAtiva();
        if (!pagina) return;
        menuEl.querySelectorAll('[data-nav]').forEach(function (link) {
            if (link.getAttribute('data-nav') === pagina) {
                link.classList.add('active');
            }
        });
    }

    /* ── 3. Injeta um bloco no marcador da página ──────────
       Pega o innerHTML de #bloco-X do template e coloca
       dentro do #tpl-X da página atual.
    ─────────────────────────────────────────────────────── */
    function injetar(templateDoc, blocoId, alvoId) {
        var bloco = templateDoc.getElementById(blocoId);
        var alvo  = document.getElementById(alvoId);
        if (!bloco || !alvo) return;
        alvo.innerHTML = bloco.innerHTML;
    }

    /* ── 4. Efeito de scroll no header ─────────────────────
       Fica aqui para não precisar repetir em cada página.
    ─────────────────────────────────────────────────────── */
    function ativarScrollHeader() {
        window.addEventListener('scroll', function () {
            var header = document.querySelector('.header');
            if (!header) return;
            if (window.scrollY > 100) {
                header.style.padding    = '15px 0';
                header.style.background = 'rgba(62,39,35,.98)';
            } else {
                header.style.padding    = '20px 0';
                header.style.background = 'linear-gradient(180deg,rgba(62,39,35,.95) 0%,rgba(62,39,35,.85) 100%)';
            }
        }, { passive: true });
    }

    /* ── 5. Preenche o ano do copyright ────────────────────*/
    function preencherAno() {
        var el = document.getElementById('tpl-ano');
        if (el) el.textContent = new Date().getFullYear();
    }

    /* ── 6. Lógica principal: faz o fetch ──────────────────*/
    function carregar() {
        /* Descobre o caminho para template.html.
           Páginas na raiz usam  "template.html";
           páginas em subpastas usam  "../template.html".
           Aqui simplesmente tentamos na raiz. */
        var url = 'template.html';

        fetch(url)
            .then(function (resp) {
                if (!resp.ok) throw new Error('template.html não encontrado (' + resp.status + ')');
                return resp.text();
            })
            .then(function (html) {
                /* Cria um documento temporário para parsear o HTML */
                var parser = new DOMParser();
                var tplDoc = parser.parseFromString(html, 'text/html');

                /* Injeta cada bloco no marcador correto */
                injetar(tplDoc, 'bloco-whatsapp', 'tpl-whatsapp');
                injetar(tplDoc, 'bloco-menu',     'tpl-menu');
                injetar(tplDoc, 'bloco-rodape',   'tpl-rodape');
                injetar(tplDoc, 'bloco-carrinho', 'tpl-carrinho');

                /* Ajustes pós-injeção */
                marcarAtivo(document);
                preencherAno();
                ativarScrollHeader();

                /* Avisa outros scripts que o template foi carregado */
                window.dispatchEvent(new Event('templateCarregado'));
            })
            .catch(function (erro) {
                console.warn('[template.js]', erro.message);
                /* Mesmo com erro, avisa os outros scripts para não travar */
                window.dispatchEvent(new Event('templateCarregado'));
            });
    }

    /* Executa quando o DOM estiver pronto */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', carregar);
    } else {
        carregar();
    }

})();