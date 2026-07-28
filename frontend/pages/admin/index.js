import React from 'react';
import Head from 'next/head';
import { useState } from 'react';
import { useRouter } from 'next/router';
import api from '../../lib/api';
import Link from 'next/link';
import Button from '../../components/Button';
import Card from '../../components/Card';
import FormGroup from '../../components/FormGroup';

export default function AdminLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username.trim() || !password.trim()) {
      setError('Por favor, preencha todos os campos.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/api/login', {
        username,
        password
      });
      
      if (response.data.success) {
        // Store user in localStorage or context
        localStorage.setItem('user', response.data.user);
        router.push('/admin/dashboard');
      } else {
        setError('Usuário ou senha inválidos.');
      }
    } catch (err) {
      console.error('Error logging in:', err);
      setError('Erro ao realizar login. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-light min-h-screen">
      <Head>
        <title>Login - Sistema de Triagem HCI</title>
        <meta name="description" content="Login para o Sistema de Triagem do Hospital de Clínicas Ijuí" />
        <link rel="icon" href="/images/favicon.png" />
      </Head>

      <div className="container" style={{ position: 'relative' }}>
        <Link href="/">
          <Button 
            variant="secondary"
            className="mt-4"
          >
            ← VOLTAR PARA TRIAGEM
          </Button>
        </Link>

        <div className="text-center mt-4 mb-4">
          <img 
            src="/images/hci_logo.png" 
            alt="Logo HCI" 
            style={{ maxWidth: '300px', marginBottom: '1rem' }}
          />
          <h2 className="text-primary" style={{fontSize: '1.5rem'}}>
            Painel de Validação de Triagens
          </h2>
        </div>

        <div className="login-container">
          <h2 className="login-title">Login do Sistema</h2>
          
          <form onSubmit={handleSubmit}>
            <FormGroup
              label="Usuário"
              htmlFor="username"
            >
              <input
                id="username"
                type="text"
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Digite seu usuário"
              />
            </FormGroup>
            
            <FormGroup
              label="Senha"
              htmlFor="password"
              error={error}
            >
              <input
                id="password"
                type="password"
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Digite sua senha"
              />
            </FormGroup>
            
            <Button 
              type="submit" 
              fullWidth
              className="login-button"
              disabled={loading}
            >
              {loading ? 'ENTRANDO...' : 'ENTRAR'}
            </Button>
          </form>
        </div>

        <Card className="mt-4 mb-4 text-center">
          <h3 className="mb-3">Credenciais para Demonstração</h3>
          <div className="d-flex justify-center flex-wrap">
            <div className="p-2 m-2 bg-light rounded">
              <strong>Admin:</strong><br />
              admin / admin
            </div>
            <div className="p-2 m-2 bg-light rounded">
              <strong>Médico:</strong><br />
              medico / medico
            </div>
            <div className="p-2 m-2 bg-light rounded">
              <strong>Enfermeiro:</strong><br />
              enfermeiro / enfermeiro
            </div>
          </div>
        </Card>

        <footer className="footer">
          <p className="mb-1"><strong>Sistema de Validação de Triagens Clínicas</strong></p>
          <p className="mb-1">Hospital de Clínicas de Ijuí</p>
          <p className="mb-1">© {new Date().getFullYear()} - Todos os direitos reservados</p>
        </footer>
      </div>
    </div>
  );
}
