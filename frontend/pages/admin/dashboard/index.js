import { useState, useEffect, useCallback } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import api from '../../../lib/api';
import Modal from '../../../components/Modal';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [activeMenu, setActiveMenu] = useState('dashboard');
  const [stats, setStats] = useState({ total: 0, validadas: 0, pendentes: 0 });
  const [triagens, setTriagens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [validatingTriagem, setValidatingTriagem] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMessage, setModalMessage] = useState('');
  const router = useRouter();

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const statsResponse = await api.get('/api/estatisticas');
      setStats(statsResponse.data);

      // Load triagens based on active menu
      if (activeMenu === 'dashboard' || activeMenu === 'pendentes') {
        const triagensResponse = await api.get('/api/triagens?filtro=pendentes');
        setTriagens(triagensResponse.data.triagens);
      } else if (activeMenu === 'todas') {
        const triagensResponse = await api.get('/api/triagens?filtro=todas');
        setTriagens(triagensResponse.data.triagens);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Erro ao carregar dados. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  }, [activeMenu]);

  // Bootstrap client-only: localStorage não existe no prerender, então a sessão
  // só pode ser lida depois da montagem. Roda uma vez — trocar de menu já
  // dispara o fetch por handleMenuClick, então não entra nas dependências.
  useEffect(() => {
    const loggedInUser = localStorage.getItem('user');
    if (!loggedInUser) {
      router.push('/admin');
      return;
    }

    // eslint-disable-next-line react-hooks/set-state-in-effect -- sessão só é legível após a montagem
    setUser(loggedInUser);
    fetchDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- roda só na montagem, de propósito
  }, []);

  const handleMenuClick = async (menu) => {
    setActiveMenu(menu);
    setLoading(true);
    
    try {
      if (menu === 'pendentes') {
        const response = await api.get('/api/triagens?filtro=pendentes');
        setTriagens(response.data.triagens);
      } else if (menu === 'todas') {
        const response = await api.get('/api/triagens?filtro=todas');
        setTriagens(response.data.triagens);
      } else if (menu === 'dashboard') {
        await fetchDashboardData();
      }
    } catch (err) {
      console.error('Error changing menu:', err);
      setError('Erro ao carregar dados. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (triagem) => {
    if (!triagem || !triagem.id) return;
    setValidatingTriagem(triagem);
    setFeedback('');
  };

  const submitValidation = async () => {
    if (!feedback.trim()) {
      setModalMessage('Por favor, digite um feedback.');
      setModalOpen(true);
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await api.post('/api/validar', {
        triagem_id: validatingTriagem.id,
        validado_por: user,
        feedback
      });
      
      if (response.data.success) {
        setModalMessage('Triagem validada com sucesso!');
        setModalOpen(true);
        setValidatingTriagem(null);
        setFeedback('');
        fetchDashboardData(); // Refresh data
      } else {
        setModalMessage('Erro ao validar triagem. Por favor, tente novamente.');
        setModalOpen(true);
      }
    } catch (err) {
      console.error('Error validating triage:', err);
      setModalMessage('Erro ao validar triagem. Por favor, tente novamente.');
      setModalOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const cancelValidation = () => {
    setValidatingTriagem(null);
    setFeedback('');
  };

  // Função para formatar data de forma segura
  const formatDate = (dateString) => {
    if (!dateString) return 'Data não disponível';
    
    try {
      const date = new Date(dateString);
      // Verifica se a data é válida
      if (isNaN(date.getTime())) {
        return 'Data não disponível';
      }
      return date.toLocaleString();
    } catch (error) {
      console.error('Erro ao formatar data:', error);
      return 'Data não disponível';
    }
  };

  // Função para truncar texto com segurança
  const truncateText = (text, maxLength = 100) => {
    if (!text) return 'Não disponível';
    if (text.length <= maxLength) return text;
    return `${text.substring(0, maxLength)}...`;
  };

  const getClassificationColor = (classification) => {
    if (!classification) return '';
    
    const classLower = classification.toLowerCase();
    if (classLower === 'vermelho') return 'classification-red';
    if (classLower === 'laranja') return 'classification-orange';
    if (classLower === 'amarelo') return 'classification-yellow';
    if (classLower === 'verde') return 'classification-green';
    if (classLower === 'azul') return 'classification-blue';
    return '';
  };

  const getClassificationText = (classification) => {
    if (!classification) return 'NÃO CLASSIFICADO';
    
    const classLower = classification.toLowerCase();
    if (classLower === 'vermelho') return 'EMERGÊNCIA (VERMELHO)';
    if (classLower === 'laranja') return 'MUITO URGENTE (LARANJA)';
    if (classLower === 'amarelo') return 'URGENTE (AMARELO)';
    if (classLower === 'verde') return 'POUCO URGENTE (VERDE)';
    if (classLower === 'azul') return 'NÃO URGENTE (AZUL)';
    return classification.toUpperCase();
  };

  // Render validation page
  const renderValidationPage = () => {
    const triagem = validatingTriagem;
    
    return (
      <div>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '2rem' 
        }}>
          <h2 style={{ color: '#003B71', margin: 0 }}>
            Validação de Triagem
          </h2>
          <button 
            className="button button-danger"
            onClick={cancelValidation}
          >
            Cancelar
          </button>
        </div>
        
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Informações do Paciente</h3>
          </div>
          <div className="card-body">
            <p><strong>ID da Triagem:</strong> {triagem?.id || 'ID não disponível'}</p>
            <p><strong>Data:</strong> {formatDate(triagem?.data_hora)}</p>
            <p><strong>Sintomas:</strong> {triagem?.sintomas || 'Sintomas não disponíveis'}</p>
          </div>
        </div>
        
        <div className="card mt-3">
          <div className="card-header">
            <h3 className="card-title">Resultado da Triagem</h3>
          </div>
          <div className="card-body">
            <div className={`classification ${getClassificationColor(triagem?.classificacao)}`}>
              <h3>{getClassificationText(triagem?.classificacao)}</h3>
            </div>
            
            <div className="section">
              <h3 className="section-title">Análise Clínica</h3>
              <p>{triagem?.justificativa || 'Análise clínica não disponível'}</p>
            </div>
            
            <div className="section">
              <h3 className="section-title">Condutas Recomendadas</h3>
              <p>{triagem?.condutas || 'Condutas não disponíveis'}</p>
            </div>
          </div>
        </div>
        
        <div className="card mt-3">
          <div className="card-header">
            <h3 className="card-title">Validação</h3>
          </div>
          <div className="card-body">
            <div className="form-group">
              <label className="form-label">Feedback da Validação</label>
              <textarea 
                className="form-textarea"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Digite seu feedback sobre esta triagem..."
              />
            </div>
            
            <div className="text-right">
              <button 
                className="button"
                onClick={submitValidation}
                disabled={loading}
              >
                {loading ? 'Processando...' : 'Validar Triagem'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Render dashboard content
  const renderDashboard = () => {
    return (
      <div>
        <div className="dashboard-header">
          <h2>Bem-vindo, {user}!</h2>
          <p>Painel de controle do Sistema de Triagem HCI</p>
        </div>
        
        <div className="stats-container">
          <div className="stat-card stat-total">
            <h3>Total de Triagens</h3>
            <h1>{stats.total}</h1>
          </div>
          
          <div className="stat-card stat-validated">
            <h3>Triagens Validadas</h3>
            <h1>{stats.validadas}</h1>
          </div>
          
          <div className="stat-card stat-pending">
            <h3>Triagens Pendentes</h3>
            <h1>{stats.pendentes}</h1>
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Triagens Recentes Pendentes de Validação</h3>
          </div>
          <div className="card-body">
            {triagens.length === 0 ? (
              <p>Não há triagens pendentes de validação.</p>
            ) : (
              <div>
                {triagens.slice(0, 5).map((triagem) => (
                  <div key={triagem.id || Math.random().toString()} className="card mb-3">
                    <div className="card-body">
                      <p><strong>Data:</strong> {formatDate(triagem.data_hora)}</p>
                      <p><strong>Sintomas:</strong> {truncateText(triagem.sintomas)}</p>
                      <p>
                        <strong>Classificação:</strong> 
                        <span className={`badge ${getClassificationColor(triagem.classificacao)}`} style={{ marginLeft: '8px' }}>
                          {getClassificationText(triagem.classificacao)}
                        </span>
                      </p>
                      <div className="text-right">
                        <button 
                          className="button"
                          onClick={() => handleValidate(triagem)}
                        >
                          Validar
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {triagens.length > 5 && (
                  <div className="text-center mt-3">
                    <button 
                      className="button button-secondary"
                      onClick={() => handleMenuClick('pendentes')}
                    >
                      Ver Todas Pendentes
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Render all triagens
  const renderTriagensList = () => {
    return (
      <div>
        <h2>{activeMenu === 'pendentes' ? 'Triagens Pendentes' : 'Todas as Triagens'}</h2>
        
        {triagens.length === 0 ? (
          <div className="card">
            <div className="card-body">
              <p>Não há triagens para exibir.</p>
            </div>
          </div>
        ) : (
          <div>
            {triagens.map((triagem) => (
              <div key={triagem.id || Math.random().toString()} className="card mb-3">
                <div className="card-body">
                  <p><strong>ID:</strong> {triagem.id || 'ID não disponível'}</p>
                  <p><strong>Data:</strong> {formatDate(triagem.data)}</p>
                  <p><strong>Sintomas:</strong> {truncateText(triagem.sintomas)}</p>
                  <p>
                    <strong>Classificação:</strong> 
                    <span className={`badge ${getClassificationColor(triagem.classificacao)}`} style={{ marginLeft: '8px' }}>
                      {getClassificationText(triagem.classificacao)}
                    </span>
                  </p>
                  <p><strong>Status:</strong> {triagem.validado ? 'Validado' : 'Pendente'}</p>
                  
                  {!triagem.validado && (
                    <div className="text-right">
                      <button 
                        className="button"
                        onClick={() => handleValidate(triagem)}
                      >
                        Validar
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <Head>
        <title>Dashboard - Sistema de Triagem HCI</title>
        <meta name="description" content="Dashboard administrativo do Sistema de Triagem HCI" />
      </Head>

      {/* Navbar Superior */}
      <div className="navbar">
        <div className="navbar-brand">
          <h3>Sistema de Triagem</h3>
          <p>Painel Administrativo</p>
        </div>
        
        <div className="navbar-menu">
          <a 
            className={`navbar-link ${activeMenu === 'dashboard' ? 'active' : ''}`}
            onClick={() => handleMenuClick('dashboard')}
          >
            Dashboard
          </a>
          <a 
            className={`navbar-link ${activeMenu === 'pendentes' ? 'active' : ''}`}
            onClick={() => handleMenuClick('pendentes')}
          >
            Triagens Pendentes
          </a>
          <a 
            className={`navbar-link ${activeMenu === 'todas' ? 'active' : ''}`}
            onClick={() => handleMenuClick('todas')}
          >
            Todas as Triagens
          </a>
          <a 
            className="navbar-link"
            onClick={() => {
              localStorage.removeItem('user');
              router.push('/admin');
            }}
          >
            Sair
          </a>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="main-content">
        {loading && !validatingTriagem ? (
          <div className="text-center p-5">
            <p>Carregando...</p>
          </div>
        ) : error ? (
          <div className="alert alert-danger">
            {error}
          </div>
        ) : validatingTriagem ? (
          renderValidationPage()
        ) : activeMenu === 'dashboard' ? (
          renderDashboard()
        ) : (
          renderTriagensList()
        )}
      </div>
      
      {/* Modal de Notificação */}
      <Modal 
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        message={modalMessage}
      />
    </div>
  );
}
