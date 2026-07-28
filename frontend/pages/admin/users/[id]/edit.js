import React from 'react';
import Head from 'next/head';
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import api from '../../../../lib/api';
import Header from '../../../../components/Header';
import Footer from '../../../../components/Footer';
import Button from '../../../../components/Button';
import Card from '../../../../components/Card';
import FormGroup from '../../../../components/FormGroup';

export default function EditUser() {
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: '',
    ativo: true
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const router = useRouter();
  const { id } = router.query;
  
  const fetchUserData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/usuarios/${id}`);

      if (response.data.success) {
        const userData = response.data.usuario;
        setFormData({
          nome: userData.nome,
          email: userData.email,
          password: '',
          confirmPassword: '',
          role: userData.role,
          ativo: userData.ativo
        });
      } else {
        setError('Usuário não encontrado');
      }
    } catch (err) {
      console.error('Error fetching user data:', err);
      setError('Erro ao carregar dados do usuário');
    } finally {
      setLoading(false);
    }
  }, [id]);

  // Check if user is logged in and has admin privileges
  useEffect(() => {
    const user = localStorage.getItem('user');
    if (!user || user !== 'admin') {
      router.push('/admin');
      return;
    }

    // Fetch user data if ID is available
    if (id) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- carga inicial marca loading antes do await
      fetchUserData();
    }
  }, [router, id, fetchUserData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const validateForm = () => {
    if (!formData.nome.trim()) {
      setError('Por favor, informe o nome completo.');
      return false;
    }
    
    if (!formData.email.trim() || !formData.email.includes('@')) {
      setError('Por favor, informe um email válido.');
      return false;
    }
    
    if (formData.password && formData.password !== formData.confirmPassword) {
      setError('As senhas não coincidem.');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setSaving(true);
    setError('');
    
    try {
      // Preparar dados para envio (excluir confirmPassword)
      const { confirmPassword, ...dataToSend } = formData;
      
      // Se a senha estiver vazia, não enviar
      if (!dataToSend.password) {
        delete dataToSend.password;
      }
      
      const response = await api.put(`/api/usuarios/${id}`, dataToSend);
      
      if (response.data.success) {
        setSuccess(true);
      } else {
        setError(response.data.message || 'Erro ao atualizar usuário.');
      }
    } catch (err) {
      console.error('Error updating user:', err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Erro ao atualizar usuário. Por favor, tente novamente.');
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-light min-h-screen">
      <Head>
        <title>Editar Usuário - Sistema de Triagem HCI</title>
        <meta name="description" content="Edição de Usuário do Sistema de Triagem do Hospital de Clínicas Ijuí" />
        <link rel="icon" href="/images/favicon.png" />
      </Head>

      <div className="container">
        <Header showAdminButton={false} />
        
        <div className="header-gradient rounded-lg p-4 text-center mb-4">
          <h1>Editar Usuário</h1>
          <p className="text-white">Atualização de dados de acesso</p>
        </div>
        
        <div className="d-flex justify-between mb-4">
          <Button 
            variant="secondary" 
            onClick={() => router.push('/admin/users')}
          >
            ← Voltar para Lista de Usuários
          </Button>
        </div>

        {loading ? (
          <Card>
            <div className="text-center p-4">
              <p>Carregando dados do usuário...</p>
            </div>
          </Card>
        ) : (
          <Card title="Editar Dados do Usuário">
            {success ? (
              <div className="alert alert-success">
                <p><strong>Usuário atualizado com sucesso!</strong></p>
                <p>As alterações foram salvas no sistema.</p>
                <div className="mt-3">
                  <Button onClick={() => router.push('/admin/users')}>
                    Voltar para Lista de Usuários
                  </Button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                <FormGroup
                  label="Nome Completo"
                  htmlFor="nome"
                >
                  <input
                    id="nome"
                    name="nome"
                    type="text"
                    className="form-input"
                    value={formData.nome}
                    onChange={handleChange}
                    placeholder="Ex: João da Silva"
                  />
                </FormGroup>
                
                <FormGroup
                  label="Email"
                  htmlFor="email"
                >
                  <input
                    id="email"
                    name="email"
                    type="email"
                    className="form-input"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="Ex: joao.silva@email.com"
                  />
                </FormGroup>
                
                <div className="d-flex space-between">
                  <FormGroup
                    label="Nova Senha (deixe em branco para manter a atual)"
                    htmlFor="password"
                    className="w-100 mr-2"
                  >
                    <input
                      id="password"
                      name="password"
                      type="password"
                      className="form-input"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Digite a nova senha"
                    />
                  </FormGroup>
                  
                  <FormGroup
                    label="Confirmar Nova Senha"
                    htmlFor="confirmPassword"
                    className="w-100 ml-2"
                  >
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      className="form-input"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="Confirme a nova senha"
                    />
                  </FormGroup>
                </div>
                
                <FormGroup
                  label="Função"
                  htmlFor="role"
                >
                  <select
                    id="role"
                    name="role"
                    className="form-select"
                    value={formData.role}
                    onChange={handleChange}
                  >
                    <option value="admin">Administrador</option>
                    <option value="medico">Médico</option>
                    <option value="enfermeiro">Enfermeiro</option>
                    <option value="recepcionista">Recepcionista</option>
                  </select>
                </FormGroup>
                
                <FormGroup
                  label="Status"
                  htmlFor="ativo"
                >
                  <div className="d-flex align-center">
                    <input
                      id="ativo"
                      name="ativo"
                      type="checkbox"
                      checked={formData.ativo}
                      onChange={handleChange}
                      style={{ marginRight: '10px', width: 'auto' }}
                    />
                    <label htmlFor="ativo">Usuário ativo</label>
                  </div>
                </FormGroup>
                
                {error && (
                  <div className="alert alert-danger mb-3">
                    {error}
                  </div>
                )}
                
                <div className="d-flex justify-between mt-4">
                  <Button 
                    type="button" 
                    variant="secondary"
                    onClick={() => router.push('/admin/users')}
                  >
                    Cancelar
                  </Button>
                  
                  <Button 
                    type="submit" 
                    disabled={saving}
                  >
                    {saving ? 'Salvando...' : 'Salvar Alterações'}
                  </Button>
                </div>
              </form>
            )}
          </Card>
        )}

        <Footer />
      </div>
    </div>
  );
}
