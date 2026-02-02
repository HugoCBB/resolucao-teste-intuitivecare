import axios from "axios";


const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    "Content-Type": "application/json",
  }
})

export const getOperadoras = async (page = 1, limit = 10, search = '') => {
  let url = `/operadoras?page=${page}&limit=${limit}`;
  if (search) {
    url += `&search=${search}`;
  }
  const response = await api.get(url)
  return response.data
}

export const getEstatisticas = async () => {
  const response = await api.get('/estatisticas')
  return response.data
}

export const getDespesasOperadora = async (cnpj: string) => {
  const response = await api.get(`/operadoras/${cnpj}/despesas`)
  return response.data
}


export default api;