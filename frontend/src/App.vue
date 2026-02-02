<script setup lang="ts">
 import { ref, onMounted, watch } from 'vue';
import { getOperadoras, getEstatisticas, getDespesasOperadora } from './api';

interface Stats {
  top_5_operadoras: Array<{ registro_ans: string; razao_social: string; total_despesa: number }>;
  total_despesas: number;
}

interface Operadora {
  cnpj: string;
  razao_social: string;
  status: string;
  registro_ans: string;
}

interface Despesa {
  registro_ans: string;
  ano: number;
  trimestre: number;
  valor_despesa: number;
  modalidade: string;
  uf: string;
}

const view = ref('lista'); 
const operadoras = ref<Operadora[]>([]);
const stats = ref<Stats | null>(null);
const despesas = ref<Despesa[]>([]); 
const operadoraAtual = ref(''); 
const pagina = ref(1);
const busca = ref('');
const loading = ref(false);

const carregarTudo = async () => {
  loading.value = true;
  try {
    operadoras.value = await getOperadoras(pagina.value, 10, busca.value);
    stats.value = await getEstatisticas();
  } finally {
    loading.value = false;
  }
};

watch(busca, async (novoValor) => {
    pagina.value = 1;
    loading.value = true;
    try {
        operadoras.value = await getOperadoras(pagina.value, 10, novoValor);
    } finally {
        loading.value = false;
    }
});

const abrirDetalhes = async (op: any) => {
  loading.value = true;
  operadoraAtual.value = `${op.razao_social}`;
  try {
    despesas.value = await getDespesasOperadora(op.cnpj);
    view.value = 'detalhes';
  } finally {
    loading.value = false;
  }
};

const mudarPagina = async (novaPagina: number) => {
  if (novaPagina < 1) return;
  pagina.value = novaPagina;
  operadoras.value = await getOperadoras(pagina.value, 10, busca.value);
};

onMounted(() => {
  carregarTudo();
});
</script>

<template>
  <nav class="navbar navbar-dark bg-primary mb-4">
    <div class="container">
      <span class="navbar-brand mb-0 h1">Dashboard ANS</span>
    </div>
  </nav>
  <main class="container">
    
    <div v-if="loading" class="alert alert-info text-center">
      Carregando dados...
    </div>

    <div v-if="view === 'lista' && !loading">
      
      <div class="card mb-4 shadow-sm" v-if="stats">
        <div class="card-header bg-light fw-bold">
          Top 5 Despesas por Operadora
        </div>
        <div class="card-body">
          <div v-for="item in stats.top_5_operadoras" :key="item.registro_ans" class="mb-3">
            <div class="d-flex justify-content-between small mb-1">
              <span>{{ item.razao_social.substring(0, 30) }}...</span>
              <span class="fw-bold">R$ {{ item.total_despesa.toLocaleString('pt-BR') }}</span>
            </div>
            <div class="progress" style="height: 10px;">
              <div 
                class="progress-bar bg-success" 
                role="progressbar" 
                :style="{ width: (item.total_despesa / stats.total_despesas * 100) + '%' }"
              ></div>
            </div>
          </div>
          <hr>
          <p class="text-end text-muted mb-0">Total Geral: R$ {{ stats.total_despesas.toLocaleString('pt-BR') }}</p>
        </div>
      </div>

      <div class="row mb-3">
        <div class="col">
          <input 
            v-model="busca" 
            type="text" 
            class="form-control" 
            placeholder="Filtrar por Razão Social ou CNPJ..."
          />
        </div>
      </div>

      <div class="card shadow-sm">
        <div class="card-body p-0">
          <table class="table table-striped table-hover mb-0">
            <thead class="table-dark">
              <tr>
                <th>CNPJ</th>
                <th>Razão Social</th>
                <th class="text-center">Status</th>
                <th class="text-end">Ação</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="op in operadoras" :key="op.cnpj">
                <td>{{ op.cnpj }}</td>
                <td>{{ op.razao_social }}</td>
                <td class="text-center">
                  <span 
                    class="badge rounded-pill" 
                    :class="op.status.includes('Ativa') ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ op.status }}
                  </span>
                </td>
                <td class="text-end">
                  <button class="btn btn-sm btn-outline-primary" @click="abrirDetalhes(op)">
                    Detalhes
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="d-flex justify-content-center mt-4 gap-2">
        <button class="btn btn-secondary" @click="mudarPagina(pagina - 1)" :disabled="pagina <= 1">
          &laquo; Anterior
        </button>
        <span class="align-self-center fw-bold">Pág. {{ pagina }}</span>
        <button class="btn btn-secondary" @click="mudarPagina(pagina + 1)">
          Próxima &raquo;
        </button>
      </div>
    </div>

    <div v-else-if="view === 'detalhes' && !loading">
      <button class="btn btn-outline-secondary mb-3" @click="view = 'lista'">
        &larr; Voltar para Lista
      </button>

      <div class="card">
        <div class="card-header bg-primary text-white">
          <h5 class="mb-0">{{ operadoraAtual }}</h5>
        </div>
        <div class="card-body">
          <h6 class="card-title">Histórico de Despesas</h6>
          
          <div v-if="despesas.length === 0" class="alert alert-warning">
            Nenhuma despesa registrada para esta operadora.
          </div>

          <ul v-else class="list-group list-group-flush">
            <li v-for="d in despesas" :key="d.registro_ans + d.ano + d.trimestre" class="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>{{ d.ano }} - {{ d.trimestre }}º Trimestre</strong>
                <div class="text-muted small">Modalidade: {{ d.modalidade }} | UF: {{ d.uf }}</div>
              </div>
              <span class="badge bg-primary rounded-pill">
                R$ {{ d.valor_despesa.toLocaleString('pt-BR') }}
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>

  </main>
</template>

<style scoped>
</style>
