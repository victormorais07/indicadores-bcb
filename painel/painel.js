// Painel dos indicadores. Lê os CSV da pasta dados/ (os mesmos que o GitHub Actions atualiza)
// e desenha os gráficos com Chart.js.

const dados = {};
const graficos = {};
let mesesSelecionados = 12;

const cor = (nome) => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();

async function carregarCsv(nome) {
  const resp = await fetch(`dados/${nome}.csv`, { cache: "no-cache" });
  if (!resp.ok) throw new Error(`não consegui ler dados/${nome}.csv`);

  const linhas = (await resp.text()).trim().split(/\r?\n/).slice(1);
  return linhas.map((linha) => {
    const [data, valor] = linha.split(",");
    return { data: new Date(data + "T00:00:00"), valor: Number(valor) };
  });
}

// ---------- formatação ----------

function numero(valor, casas = 2) {
  return valor.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
}

function dataBr(data) {
  return data.toLocaleDateString("pt-BR");
}

function mesAno(data) {
  const texto = data.toLocaleDateString("pt-BR", { month: "long", year: "numeric" });
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function variacao(percentual) {
  const sinal = percentual > 0 ? "+" : "";
  const classe = percentual > 0 ? "sobe" : percentual < 0 ? "desce" : "";
  return `<span class="${classe}">${sinal}${numero(percentual)}%</span>`;
}

// ---------- período ----------

function filtrar(serie, meses) {
  if (!meses) return serie;
  const ultima = serie[serie.length - 1].data;
  const corte = new Date(ultima);
  corte.setMonth(corte.getMonth() - meses);
  return serie.filter((p) => p.data >= corte);
}

function nomePeriodo(meses) {
  if (!meses) return "desde 2020";
  if (meses < 12) return meses === 1 ? "no último mês" : `nos últimos ${meses} meses`;
  return meses === 12 ? "no último ano" : `nos últimos ${meses / 12} anos`;
}

// ---------- cards ----------

function preencherCard(id, valor, detalhe) {
  const card = document.getElementById(id);
  card.querySelector(".valor").textContent = valor;
  card.querySelector(".detalhe").innerHTML = detalhe;
}

function atualizarCards() {
  const dolar = filtrar(dados.dolar, mesesSelecionados);
  const ultimoDolar = dolar[dolar.length - 1];
  const varDolar = (ultimoDolar.valor / dolar[0].valor - 1) * 100;
  preencherCard(
    "card-dolar",
    `R$ ${numero(ultimoDolar.valor, 4)}`,
    `${variacao(varDolar)} ${nomePeriodo(mesesSelecionados)} · ${dataBr(ultimoDolar.data)}`
  );

  // a Selic é diária mas só muda nas reuniões do Copom, então procura quando foi a última mudança
  const selic = dados.selic;
  const atual = selic[selic.length - 1];
  let desde = selic[0].data;
  for (let i = selic.length - 1; i > 0; i--) {
    if (selic[i - 1].valor !== atual.valor) {
      desde = selic[i].data;
      break;
    }
  }
  preencherCard("card-selic", `${numero(atual.valor)}%`, `ao ano, desde ${dataBr(desde)}`);

  // IPCA acumulado em 12 meses: multiplica (1 + taxa) de cada mês
  const ipca = dados.ipca;
  const ultimoIpca = ipca[ipca.length - 1];
  const acumulado = ipca.slice(-12).reduce((total, p) => total * (1 + p.valor / 100), 1);
  preencherCard(
    "card-ipca",
    `${numero(ultimoIpca.valor)}%`,
    `${mesAno(ultimoIpca.data)} · ${numero((acumulado - 1) * 100)}% em 12 meses`
  );
}

// ---------- gráficos ----------

function opcoesBase(unidadeTempo, formatarValor) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          title: (itens) => {
            const data = new Date(itens[0].parsed.x);
            return unidadeTempo === "month" ? mesAno(data) : dataBr(data);
          },
          label: (item) => formatarValor(item.parsed.y),
        },
      },
    },
    scales: {
      x: {
        type: "time",
        time: { tooltipFormat: "dd/MM/yyyy", displayFormats: { day: "dd/MM", month: "MM/yyyy", year: "yyyy" } },
        grid: { display: false },
        ticks: { color: cor("--suave"), maxTicksLimit: 8 },
      },
      y: {
        grid: { color: cor("--borda") },
        ticks: { color: cor("--suave") },
      },
    },
  };
}

function criarGraficos() {
  graficos.dolar = new Chart(document.getElementById("grafico-dolar"), {
    type: "line",
    data: { datasets: [{ data: [], borderColor: cor("--verde"), borderWidth: 1.5, pointRadius: 0 }] },
    options: opcoesBase("day", (v) => `R$ ${numero(v, 4)}`),
  });

  graficos.selic = new Chart(document.getElementById("grafico-selic"), {
    type: "line",
    data: { datasets: [{ data: [], borderColor: cor("--azul"), borderWidth: 2, pointRadius: 0, stepped: true }] },
    options: opcoesBase("day", (v) => `${numero(v)}% a.a.`),
  });

  graficos.ipca = new Chart(document.getElementById("grafico-ipca"), {
    type: "bar",
    data: { datasets: [{ data: [], backgroundColor: [] }] },
    options: opcoesBase("month", (v) => `${numero(v)}%`),
  });
}

function paraPontos(serie) {
  return serie.map((p) => ({ x: p.data, y: p.valor }));
}

function atualizarGraficos() {
  graficos.dolar.data.datasets[0].data = paraPontos(filtrar(dados.dolar, mesesSelecionados));
  graficos.selic.data.datasets[0].data = paraPontos(filtrar(dados.selic, mesesSelecionados));

  // IPCA é mensal, com 1 ou 6 meses quase não aparece nada, então mostra pelo menos 1 ano
  const mesesIpca = mesesSelecionados && Math.max(mesesSelecionados, 12);
  const ipca = filtrar(dados.ipca, mesesIpca);
  graficos.ipca.data.datasets[0].data = paraPontos(ipca);
  graficos.ipca.data.datasets[0].backgroundColor = ipca.map((p) => (p.valor < 0 ? cor("--verde") : cor("--vermelho")));

  Object.values(graficos).forEach((g) => g.update());
}

// ---------- início ----------

function selecionarPeriodo(evento) {
  const botao = evento.target.closest("button");
  if (!botao) return;

  document.querySelectorAll("#periodos button").forEach((b) => b.classList.remove("ativo"));
  botao.classList.add("ativo");
  mesesSelecionados = Number(botao.dataset.meses);

  atualizarCards();
  atualizarGraficos();
}

async function iniciar() {
  const aviso = document.getElementById("aviso");
  try {
    const [dolar, selic, ipca] = await Promise.all(["dolar", "selic", "ipca"].map(carregarCsv));
    Object.assign(dados, { dolar, selic, ipca });
  } catch (erro) {
    aviso.textContent = `Erro ao carregar os dados: ${erro.message}`;
    aviso.classList.add("erro");
    return;
  }
  aviso.textContent = "";

  const ultimaData = dados.dolar[dados.dolar.length - 1].data;
  document.getElementById("atualizado").textContent = dataBr(ultimaData);

  criarGraficos();
  atualizarCards();
  atualizarGraficos();
  document.getElementById("periodos").addEventListener("click", selecionarPeriodo);
}

iniciar();
