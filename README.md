# CloudProject
Aluno: Pedro Paulo Mendonça Telho

Um sistema ORM multi-cloud com Load Balancer e Autoscalling.
1. Implementar comunicação via REST API.
2. Autenticação de usuário stateless.
3. Sistema de log das atividades.
4. Possuir um aplicação cliente.
5. Possuir um script de implantação automático (sem intervenção manual).

### Baixar dependências
```bash
pip install -r requirements.txt
```

### Rodando o script
```bash
python3 main.py
```


### Utilizando os serviços
#### Comandos:
<ul>
  <li>get-tasks: lista as tasks</li>
  <li>post: criar nova task</li>
  <li>update: atualizar task</li>
  <li>delete: deletar task</li>
</ul>

```bash
./script <comando> --help
```
