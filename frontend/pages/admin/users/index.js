import React from 'react';
import Head from 'next/head';
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import api from '../../../lib/api';
import Header from '../../../components/Header';
import Footer from '../../../components/Footer';
import Button from '../../../components/Button';
import Card from '../../../components/Card';

export default function UsersList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();
  
  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/usuarios');
      setUsers(response.data.usuarios);
      setError('');
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Erro ao carregar usuários. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Check if user is logged in and has admin privileges
  useEffect(() => {
    const user = localStorage.getItem('user');
    if (!user || user !== 'admin') {
      router.push('/admin');
      return;
    }

    // eslint-disable-next-line react-hooks/set-state-in-effect -- carga inicial marca loading antes do await
    fetchUsers();
  }, [router, fetchUsers]);

  const handleDelete = async (userId) => {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) {
      return;
    }
    
    try {
      const response = await api.delete(`/api/usuarios/${userId}`);
      
      if (response.data.success) {
        // Atualizar lista de usuários
        fetchUsers();
      } else {
        setError(response.data.message || 'Erro ao excluir usuário.');
      }
    } catch (err) {
      console.error('Error deleting user:', err);
      setError('Erro ao excluir usuário. Por favor, tente novamente.');
    }
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case 'admin':
        return <span className="badge badge-info">Administrador</span>;
      case 'medico':
        return <span className="badge badge-success">Médico</span>;
      case 'enfermeiro':
        return <span className="badge badge-warning">Enfermeiro</span>;
      case 'recepcionista':
        return <span className="badge badge-danger">Recepcionista</span>;
      default:
        return <span className="badge">{role}</span>;
    }
  };

  return (
    <div className="bg-light min-h-screen">
      <Head>
        <title>Gerenciar Usuários - Sistema de Triagem HCI</title>
        <meta name="description" content="Gerenciamento de Usuários do Sistema de Triagem do Hospital de Clínicas Ijuí" />
        <link rel="icon" href="/images/favicon.png" />
      </Head>

      <div className="container">
        <Header showAdminButton={false} />
        
        <div className="header-gradient rounded-lg p-4 text-center mb-4">
          <h1>Gerenciamento de Usuários</h1>
          <p className="text-white">Controle de acesso ao Sistema de Triagem</p>
        </div>
        
        <div className="d-flex justify-between mb-4">
          <Button 
            variant="secondary" 
            onClick={() => router.push('/admin/dashboard')}
          >
            ← Voltar para Dashboard
          </Button>
          
          <Button 
            onClick={() => router.push('/admin/users/new')}
          >
            + Novo Usuário
          </Button>
        </div>

        {error && (
          <div className="alert alert-danger mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <Card>
            <div className="text-center p-4">
              <p>Carregando usuários...</p>
            </div>
          </Card>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Usuário</th>
                  <th>Email</th>
                  <th>Função</th>
                  <th>Status</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center">Nenhum usuário encontrado</td>
                  </tr>
                ) : (
                  users.map(user => (
                    <tr key={user.id}>
                      <td>{user.nome}</td>
                      <td>{user.username}</td>
                      <td>{user.email}</td>
                      <td>{getRoleBadge(user.role)}</td>
                      <td>
                        {user.ativo ? (
                          <span className="badge badge-success">Ativo</span>
                        ) : (
                          <span className="badge badge-danger">Inativo</span>
                        )}
                      </td>
                      <td>
                        <div className="d-flex">
                          <Button 
                            variant="secondary"
                            className="mr-2 p-1"
                            onClick={() => router.push(`/admin/users/${user.id}/edit`)}
                          >
                            Editar
                          </Button>
                          <Button 
                            variant="danger"
                            className="p-1"
                            onClick={() => handleDelete(user.id)}
                          >
                            Excluir
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        <Footer />
      </div>
    </div>
  );
}
