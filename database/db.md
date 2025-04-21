# **Explicação das Abordagens por Função**

1. **`init_db`**
   - **Abordagem**: ORM puro (`Base.metadata.create_all`).
   - **Motivo**: Operação de schema sempre usa ORM.

2. **`add_task`**
   - **Abordagem**: ORM puro (`session.add()`).
   - **Motivo**: Trabalha diretamente com o objeto Python e permite retornar a tarefa criada (incluindo o ID gerado).

3. **`get_tasks`**
   - **Abordagem**: ORM puro (`select(TaskModel)`).
   - **Motivo**: Retorna objetos Python (`TaskModel`), facilitando o uso dos dados (ex: `task.name` em vez de `task[1]`).

4. **`delete_task`**
   - **Abordagem**: Híbrida (`delete()` do Core via ORM).
   - **Motivo**: Operação direta no banco sem carregar o objeto é mais eficiente para deleção.

5. **`update_task_status`**
   - **Abordagem**: ORM puro (`session.get()` + atributo).
   - **Motivo**: Mais intuitivo para atualizar campos específicos e permite validações futuras.

---

### **Benefícios da Refatoração**

- **Consistência**: Prioriza o ORM, exceto em casos onde o Core oferece vantagens claras (como deleção).
- **Legibilidade**: Código mais expressivo (ex: `task.completed = True` em vez de SQL explícito).
- **Manutenção**: Facilita a adição de lógica adicional (ex: hooks `@validates` do SQLAlchemy).

### **Observação sobre Performance**

- Para operações em massa (ex: atualizar 1000 tarefas), substitua `update_task_status` por uma abordagem híbrida com `update().values()`.
