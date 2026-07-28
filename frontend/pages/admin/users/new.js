import React from 'react';
import Head from 'next/head';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import api from '../../../lib/api';
import Header from '../../../components/Header';
import Footer from '../../../components/Footer';
import Button from '../../../components/Button';
import Card from '../../../components/Card';
import FormGroup from '../../../components/FormGroup';

export default function UserRegistration() {
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    role: 'enfermeiro' // Default role
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const router = useRouter();
  
  // Check if user is logged in and has admin privileges
  useEffect(() => {
    const user = localStorage.getItem('user');
    if (!user || user !== 'admin') {
      router.push('/admin');
    }
  }, [router]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      setError('Por favor, informe o nome completo.');
      return false;
    }
    
    if (!formData.username.trim()) {
      setError('Por favor, informe o nome de usuário.');
      return false;
    }
    
    if (!formData.password.trim()) {
      setError('Por favor, informe uma senha.');
      return false;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('As senhas não coincidem.');
      return false;
    }
    
    if (!formData.email.trim() || !formData.email.includes('@')) {
      setError('Por favor, informe um email válido.');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Endpoint será implementado no backend
      const response = await api.post('/api/usuarios', {
        name: formData.name,
        username: formData.username,
        password: formData.password,
        email: formData.email,
        role: formData.role
      });
      
      if (response.data.success) {
        setSuccess(true);
        // Limpar formulário
        setFormData({
          name: '',
          username: '',
          password: '',
          confirmPassword: '',
          email: '',
          role: 'enfermeiro'
        });
      } else {
        setError(response.data.message || 'Erro ao cadastrar usuário.');
      }
    } catch (err) {
      console.error('Error registering user:', err);
      if (err.response && err.response.data && err.response.data.message) {
        setError(err.response.data.message);
      } else {
        setError('Erro ao cadastrar usuário. Por favor, tente novamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-light min-h-screen">
      <Head>
        <title>Cadastro de Usuários - Sistema de Triagem HCI</title>
        <meta name="description" content="Cadastro de Usuários para o Sistema de Triagem do Hospital de Clínicas Ijuí" />
        <link rel="icon" href="/images/favicon.png" />
      </Head>

      <div className="container">
        <Header showAdminButton={false} />
        
        <div className="header-gradient rounded-lg p-4 text-center mb-4">
          <h1>Cadastro de Usuários</h1>
          <p className="text-white">Gerencie o acesso ao Sistema de Triagem</p>
        </div>
        
        <div className="d-flex justify-between mb-4">
          <Button 
            variant="secondary" 
            onClick={() => router.push('/admin/dashboard')}
          >
            ← Voltar para Dashboard
          </Button>
          
          <Button 
            onClick={() => router.push('/admin/users')}
          >
            Gerenciar Usuários
          </Button>
        </div>

        <Card title="Novo Usuário">
          {success ? (
            <div className="alert alert-success">
              <p><strong>Usuário cadastrado com sucesso!</strong></p>
              <p>O novo usuário já pode acessar o sistema com as credenciais fornecidas.</p>
              <div className="mt-3">
                <Button onClick={() => setSuccess(false)}>
                  Cadastrar outro usuário
                </Button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <FormGroup
                label="Nome Completo"
                htmlFor="name"
              >
                <input
                  id="name"
                  name="name"
                  type="text"
                  className="form-input"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Ex: João da Silva"
                />
              </FormGroup>
              
              <FormGroup
                label="Nome de Usuário"
                htmlFor="username"
              >
                <input
                  id="username"
                  name="username"
                  type="text"
                  className="form-input"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Ex: joaosilva"
                />
              </FormGroup>
              
              <div className="d-flex space-between">
                <FormGroup
                  label="Senha"
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
                    placeholder="Digite a senha"
                  />
                </FormGroup>
                
                <FormGroup
                  label="Confirmar Senha"
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
                    placeholder="Confirme a senha"
                  />
                </FormGroup>
              </div>
              
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
              
              {error && (
                <div className="alert alert-danger mb-3">
                  {error}
                </div>
              )}
              
              <div className="d-flex justify-between mt-4">
                <Button 
                  type="button" 
                  variant="secondary"
                  onClick={() => router.push('/admin/dashboard')}
                >
                  Cancelar
                </Button>
                
                <Button 
                  type="submit" 
                  disabled={loading}
                >
                  {loading ? 'Cadastrando...' : 'Cadastrar Usuário'}
                </Button>
              </div>
            </form>
          )}
        </Card>

        <Footer />
      </div>
    </div>
  );
}
