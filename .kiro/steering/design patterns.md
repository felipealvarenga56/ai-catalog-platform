# Pulso Design System - Guia Completo para IA

> Este documento serve como referência para que Inteligências Artificiais possam usar corretamente os componentes do @rdsaude/pulso-react-components.

## Sumário

1. [Instalação e Configuração](#instalação-e-configuração)
   - [Requisitos de Compatibilidade](#requisitos-de-compatibilidade)
   - [Pacotes Necessários](#pacotes-necessários)
   - [Instalação](#instalação)
   - [Configuração com Next.js](#configuração-com-nextjs)
   - [Configuração com Vite](#configuração-com-vite)
2. [ThemeProvider](#themeprovider)
3. [Componentes de Layout](#componentes-de-layout)
4. [Componentes de Formulário](#componentes-de-formulário)
5. [Componentes de Feedback](#componentes-de-feedback)
6. [Componentes de Navegação](#componentes-de-navegação)
7. [Componentes de Exibição](#componentes-de-exibição)
8. [Componentes de Overlay](#componentes-de-overlay)
9. [Templates de Páginas](#templates-de-páginas)
10. [Boas Práticas](#boas-práticas)
11. [Design Tokens - Referência Completa](#design-tokens---referência-completa)
12. [Ícones Disponíveis](#ícones-disponíveis-rdicon-)
13. [Troubleshooting](#troubleshooting-resolução-de-problemas)
14. [Versões e Changelog](#versões-e-changelog)

---

## Instalação e Configuração

### Requisitos de Compatibilidade

Antes de instalar, certifique-se de que seu projeto atende aos seguintes requisitos:

| Dependência | Versão Mínima | Versão Recomendada | Notas |
|-------------|---------------|-------------------|-------|
| **Node.js** | `>=18` | `20.x LTS` | Necessário para build e desenvolvimento |
| **React** | `>=18.0.0` | `18.3.1` | Compatível com React 18+ |
| **React DOM** | `>=18.0.0` | `18.3.1` | Deve corresponder à versão do React |
| **TypeScript** | `>=4.9.0` | `5.x` | Opcional, mas recomendado |

### Pacotes Necessários

A biblioteca `@rdsaude/pulso-react-components` depende dos seguintes pacotes:

| Pacote | Descrição | Obrigatório |
|--------|-----------|-------------|
| `@rdsaude/pulso-react-components` | Componentes React do Design System | ✅ Sim |
| `@raiadrogasil/pulso-design-tokens` | Tokens de design (cores, espaçamentos, etc.) | ✅ Sim |
| `@raiadrogasil/pulso-icons` | Biblioteca de ícones | ✅ Sim |

### Instalação

```bash
# npm
npm install @rdsaude/pulso-react-components @raiadrogasil/pulso-design-tokens @raiadrogasil/pulso-icons

# yarn
yarn add @rdsaude/pulso-react-components @raiadrogasil/pulso-design-tokens @raiadrogasil/pulso-icons

# pnpm
pnpm add @rdsaude/pulso-react-components @raiadrogasil/pulso-design-tokens @raiadrogasil/pulso-icons
```

### Dependências Internas (Já incluídas na lib)

A biblioteca já inclui as seguintes dependências que você **não precisa instalar separadamente**:

| Dependência | Versão | Uso |
|-------------|--------|-----|
| `@ark-ui/react` | `5.13.0` | Componentes acessíveis headless |
| `@radix-ui/react-accordion` | `1.2.3` | Componente Accordion |
| `@radix-ui/react-dialog` | `^1.1.11` | Componentes Modal/Dialog |
| `@radix-ui/react-slot` | `1.1.0` | Pattern `asChild` para composição |
| `@radix-ui/react-switch` | `1.1.1` | Componente Switch |
| `clsx` | `2.1.1` | Utilitário para classes CSS |
| `tailwind-merge` | `2.6.0` | Merge de classes Tailwind |
| `tailwind-variants` | `0.2.1` | Variants para componentes |
| `vaul` | `^1.1.2` | Componente Drawer/BottomSheet |

### Importação dos Estilos (OBRIGATÓRIO)

**⚠️ IMPORTANTE:** Você DEVE importar os estilos CSS no ponto de entrada da sua aplicação para que os componentes funcionem corretamente:

```tsx
// No arquivo principal da aplicação (App.tsx, main.tsx, _app.tsx, etc.)
import '@rdsaude/pulso-react-components/styles.css'
```

### Importação Básica de Componentes

```tsx
// Importação centralizada (recomendado para a maioria dos casos)
import { ThemeProvider, Button, InputText, Typography } from '@rdsaude/pulso-react-components'

// Importação específica por componente (útil para tree-shaking)
import { Button } from '@rdsaude/pulso-react-components/button'
import { InputText } from '@rdsaude/pulso-react-components/input-text'
```

### Configuração com Next.js

Se você estiver usando Next.js, adicione a seguinte configuração no `next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@rdsaude/pulso-react-components'],
}

module.exports = nextConfig
```

### Configuração com Vite

Para projetos Vite, geralmente não é necessária configuração adicional. Apenas certifique-se de importar os estilos:

```tsx
// main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import '@rdsaude/pulso-react-components/styles.css'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### Configuração com Create React App (CRA)

Para projetos CRA:

```tsx
// index.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import '@rdsaude/pulso-react-components/styles.css'
import App from './App'

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement)
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

### Verificação da Instalação

Para verificar se a instalação está correta, crie um componente de teste:

```tsx
import { ThemeProvider, Button } from '@rdsaude/pulso-react-components'

function TestComponent() {
  return (
    <ThemeProvider theme="rdsaudesistemas">
      <Button.Root variant="brand-primary">
        Instalação OK!
      </Button.Root>
    </ThemeProvider>
  )
}

export default TestComponent
```

Se o botão aparecer com o estilo verde (tema RD Saúde), a instalação foi bem-sucedida!

---

## ThemeProvider

O ThemeProvider é obrigatório e deve envolver toda a aplicação. Define o tema visual do design system.

### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| theme | `'rdsaudesistemas' \| 'raia' \| 'drogasil'` | `'rdsaudesistemas'` | Tema do design system |
| children | `ReactNode` | - | Conteúdo da aplicação |

### Exemplo de Uso

```tsx
import { ThemeProvider } from '@rdsaude/pulso-react-components'

function App() {
  return (
    <ThemeProvider theme="rdsaudesistemas">
      {/* Sua aplicação aqui */}
    </ThemeProvider>
  )
}
```

---

## Componentes de Layout

### Typography

Componente para renderizar textos com estilos padronizados.

#### Subcomponentes

- `Typography.Title` - Títulos (h1-h6)
- `Typography.Subtitle` - Subtítulos
- `Typography.Body` - Texto de corpo
- `Typography.Caption` - Legendas pequenas
- `Typography.BigNumber` - Números grandes

#### Typography.Title

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| variant | `'large-bold' \| 'default-bold' \| 'small-bold'` | `'large-bold'` | Estilo do título |
| asChild | `boolean` | `false` | Renderiza como slot |

```tsx
<Typography.Title variant="large-bold">Título Principal</Typography.Title>
<Typography.Title variant="default-bold">Título Médio</Typography.Title>
<Typography.Title variant="small-bold">Título Pequeno</Typography.Title>
```

#### Typography.Body

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| variant | `'default-bold' \| 'underline-bold' \| 'default-semibold' \| 'underline-semibold' \| 'default-regular'` | `'default-bold'` | Estilo do texto |
| asChild | `boolean` | `false` | Renderiza como slot |

```tsx
<Typography.Body variant="default-regular">Texto de parágrafo normal</Typography.Body>
<Typography.Body variant="default-bold">Texto em negrito</Typography.Body>
<Typography.Body variant="underline-semibold">Texto sublinhado</Typography.Body>
```

---

## Componentes de Formulário

### Button

Componente de botão com múltiplas variantes e estados.

#### Estrutura de Composição

```tsx
import { Button } from '@rdsaude/pulso-react-components'

// Button.Root - Container principal
// Button.Icon - Ícone dentro do botão
// Button.IconDualColor - Ícone com duas cores
```

#### Button.Root Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| variant | `'brand-primary' \| 'neutral-secondary' \| 'neutral-tertiary'` | `'brand-primary'` | Variante visual |
| size | `'md' \| 'ml' \| 'lg' \| 'xl'` | `'ml'` | Tamanho do botão |
| disabled | `boolean` | `false` | Desabilita o botão |
| loading | `boolean` | `false` | Mostra spinner de loading |
| full | `boolean` | `false` | Largura 100% |
| asChild | `boolean` | `false` | Renderiza como slot |

#### Exemplos de Uso

```tsx
// Botão primário simples
<Button.Root variant="brand-primary">
  Confirmar
</Button.Root>

// Botão com ícone
<Button.Root variant="brand-primary" size="lg">
  <Button.Icon symbol="rdicon-cart" />
  Adicionar ao Carrinho
</Button.Root>

// Botão apenas com ícone
<Button.Root variant="neutral-tertiary" size="ml">
  <Button.Icon symbol="rdicon-search" />
</Button.Root>

// Botão secundário
<Button.Root variant="neutral-secondary">
  Cancelar
</Button.Root>

// Botão terciário (ghost)
<Button.Root variant="neutral-tertiary">
  Saiba mais
</Button.Root>

// Botão em loading
<Button.Root variant="brand-primary" loading>
  Processando
</Button.Root>

// Botão desabilitado
<Button.Root variant="brand-primary" disabled>
  Indisponível
</Button.Root>

// Botão full width
<Button.Root variant="brand-primary" full>
  Finalizar Compra
</Button.Root>
```

---

### InputText

Campo de texto com suporte a label, ícones e mensagens de erro.

#### Estrutura de Composição

```tsx
import { InputText } from '@rdsaude/pulso-react-components'

// InputText.Root - Container principal
// InputText.Label - Rótulo do campo
// InputText.Actions - Container para input e ações
// InputText.Field - Campo de texto
// InputText.Icon - Ícone decorativo
// InputText.ClearButton - Botão para limpar
// InputText.HelperText - Texto de ajuda/erro
```

#### InputText.Root Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'md' \| 'ml' \| 'lg' \| 'xl'` | `'ml'` | Tamanho do input |
| hasError | `boolean` | `false` | Indica estado de erro |
| disabled | `boolean` | `false` | Desabilita o campo |
| readOnly | `boolean` | `false` | Campo somente leitura |
| value | `string` | - | Valor controlado |

#### Exemplos de Uso

```tsx
// Input simples
<InputText.Root size="ml">
  <InputText.Label>E-mail</InputText.Label>
  <InputText.Actions>
    <InputText.Field placeholder="seu@email.com" />
  </InputText.Actions>
</InputText.Root>

// Input com ícone
<InputText.Root size="ml">
  <InputText.Label>Buscar</InputText.Label>
  <InputText.Actions>
    <InputText.Icon symbol="rdicon-search" />
    <InputText.Field placeholder="O que você procura?" />
  </InputText.Actions>
</InputText.Root>

// Input com erro
<InputText.Root size="ml" hasError>
  <InputText.Label>CPF</InputText.Label>
  <InputText.Actions>
    <InputText.Field placeholder="000.000.000-00" />
  </InputText.Actions>
  <InputText.HelperText withIcon iconName="rdicon-warning-circle">
    CPF inválido
  </InputText.HelperText>
</InputText.Root>

// Input com botão limpar
<InputText.Root size="ml" value={value}>
  <InputText.Label>Nome</InputText.Label>
  <InputText.Actions>
    <InputText.Field 
      value={value}
      onChange={(e) => setValue(e.target.value)} 
    />
    <InputText.ClearButton onClick={() => setValue('')} />
  </InputText.Actions>
</InputText.Root>

// Input desabilitado
<InputText.Root size="ml" disabled>
  <InputText.Label>Campo bloqueado</InputText.Label>
  <InputText.Actions>
    <InputText.Field value="Valor fixo" />
  </InputText.Actions>
</InputText.Root>
```

---

### InputPassword

Campo de senha com toggle de visibilidade.

#### Estrutura de Composição

```tsx
import { InputPassword } from '@rdsaude/pulso-react-components'

// InputPassword.Root - Container principal
// InputPassword.Label - Rótulo do campo
// InputPassword.Input - Campo de senha
// InputPassword.VisibilityTrigger - Botão para mostrar/ocultar
// InputPassword.HelperText - Texto de ajuda
```

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'md' \| 'ml' \| 'lg' \| 'xl'` | `'ml'` | Tamanho do input |
| disabled | `boolean` | `false` | Desabilita o campo |
| readOnly | `boolean` | `false` | Campo somente leitura |
| invalid | `boolean` | `false` | Estado de erro |

#### Exemplo de Uso

```tsx
<InputPassword.Root size="ml" readOnly={false}>
  <InputPassword.Label>Senha</InputPassword.Label>
  <InputPassword.Input placeholder="Digite sua senha" />
  <InputPassword.VisibilityTrigger />
  <InputPassword.HelperText>Mínimo de 8 caracteres</InputPassword.HelperText>
</InputPassword.Root>
```

---

### Checkbox

Componente de seleção múltipla.

#### Estrutura de Composição

```tsx
import { Checkbox } from '@rdsaude/pulso-react-components'

// Checkbox.Root - Container principal
// Checkbox.Label - Rótulo da opção
// Checkbox.HelperText - Texto de ajuda
// Checkbox.Parent - Container para checkboxes aninhados
```

#### Checkbox.Root Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'md' \| 'ml' \| 'lg' \| 'xl'` | `'md'` | Tamanho |
| checked | `boolean` | `false` | Estado marcado |
| indeterminate | `boolean` | `false` | Estado indeterminado |
| disabled | `boolean` | `false` | Desabilitado |
| readonly | `boolean` | `false` | Somente leitura |
| error | `boolean` | `false` | Estado de erro |
| feedbackMessage | `string` | - | Mensagem de feedback |
| onClick | `(checked: boolean) => void` | - | Handler de clique |

#### Exemplos de Uso

```tsx
// Checkbox simples
<Checkbox.Root size="ml" checked={isChecked} onClick={setIsChecked}>
  <Checkbox.Label>Aceito os termos de uso</Checkbox.Label>
</Checkbox.Root>

// Checkbox com erro
<Checkbox.Root size="ml" error feedbackMessage="Campo obrigatório" onClick={handleClick}>
  <Checkbox.Label>Li e concordo com a política de privacidade</Checkbox.Label>
</Checkbox.Root>

// Checkbox desabilitado
<Checkbox.Root size="ml" disabled checked onClick={() => {}}>
  <Checkbox.Label>Opção indisponível</Checkbox.Label>
</Checkbox.Root>

// Checkbox indeterminado (para seleção parcial)
<Checkbox.Root size="ml" indeterminate onClick={handleClick}>
  <Checkbox.Label>Selecionar todos</Checkbox.Label>
</Checkbox.Root>
```

---

### Radio

Componente de seleção única em grupo.

#### Estrutura de Composição

```tsx
import { Radio } from '@rdsaude/pulso-react-components'

// Radio.Root - Container do grupo
// Radio.Button - Botão de opção individual
// Radio.Label - Rótulo da opção
// Radio.Helper - Texto de ajuda
```

#### Radio.Root Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'md' \| 'ml' \| 'lg' \| 'xl'` | `'md'` | Tamanho |
| defaultValue | `string` | - | Valor inicial selecionado |
| disabled | `boolean` | `false` | Desabilita todo o grupo |
| readOnly | `boolean` | `false` | Somente leitura |
| error | `boolean` | `false` | Estado de erro |
| onChange | `(e: ChangeEvent) => void` | - | Handler de mudança |

#### Exemplo de Uso

```tsx
<Radio.Root 
  size="ml" 
  defaultValue="cartao"
  onChange={(e) => setPaymentMethod(e.target.value)}
>
  <Radio.Button id="cartao" name="pagamento" value="cartao">
    <Radio.Label>Cartão de Crédito</Radio.Label>
  </Radio.Button>
  <Radio.Button id="pix" name="pagamento" value="pix">
    <Radio.Label>PIX</Radio.Label>
  </Radio.Button>
  <Radio.Button id="boleto" name="pagamento" value="boleto">
    <Radio.Label>Boleto</Radio.Label>
  </Radio.Button>
</Radio.Root>
```

---

### Switch

Toggle de ligar/desligar.

#### Estrutura de Composição

```tsx
import { Switch } from '@rdsaude/pulso-react-components'

// Switch.Root - Container principal
// Switch.Toggle - Área clicável
// Switch.Thumb - Indicador visual
// Switch.Label - Rótulo
// Switch.Refresh - Indicador de loading
```

#### Switch.Root Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| disabled | `boolean` | `false` | Desabilitado |
| loading | `boolean` | `false` | Em carregamento |
| checked | `boolean` | - | Estado controlado |
| onCheckedChange | `(checked: boolean) => void` | - | Handler de mudança |

#### Exemplo de Uso

```tsx
<Switch.Root disabled={false} loading={false}>
  <Switch.Toggle>
    <Switch.Thumb />
  </Switch.Toggle>
  <Switch.Label>Ativar notificações</Switch.Label>
</Switch.Root>

// Com loading
<Switch.Root loading>
  <Switch.Toggle>
    <Switch.Refresh />
  </Switch.Toggle>
  <Switch.Label>Sincronizando...</Switch.Label>
</Switch.Root>
```

---

### Select

Componente de seleção dropdown.

#### Estrutura de Composição

```tsx
import { Select } from '@rdsaude/pulso-react-components'

// Select.Root - Container principal
// Select.Label - Rótulo
// Select.FieldContainer - Container do campo
// Select.Field - Campo de seleção
// Select.Icon - Ícone decorativo
// Select.Actions - Área de ações
// Select.HelperText - Texto de ajuda
```

#### Select.Root Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'md' \| 'ml' \| 'lg' \| 'xl'` | `'md'` | Tamanho |
| hasError | `boolean` | `false` | Estado de erro |
| disabled | `boolean` | `false` | Desabilitado |
| options | `ContentProps[]` | - | Opções disponíveis |
| placeholder | `string` | - | Texto placeholder |

#### Exemplo de Uso

```tsx
const estados = [
  { id: '1', label: 'São Paulo', value: 'SP' },
  { id: '2', label: 'Rio de Janeiro', value: 'RJ' },
  { id: '3', label: 'Minas Gerais', value: 'MG' },
]

<Select.Root size="ml" options={estados}>
  <Select.Label>Estado</Select.Label>
  <Select.FieldContainer>
    <Select.Field 
      placeholder="Selecione o estado"
      onChangeSelectionValue={(value) => setEstado(value)}
    />
  </Select.FieldContainer>
  <Select.HelperText>Escolha seu estado de residência</Select.HelperText>
</Select.Root>
```

---

### InputCounter

Campo numérico com incremento/decremento.

#### Estrutura de Composição

```tsx
import { InputCounter } from '@rdsaude/pulso-react-components'

// InputCounter.Root - Container principal
// InputCounter.Label - Rótulo
// InputCounter.Control - Container dos controles
// InputCounter.Decrement - Botão de diminuir
// InputCounter.Input - Campo numérico
// InputCounter.Increment - Botão de aumentar
// InputCounter.HelperText - Texto de ajuda
```

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'md' \| 'ml' \| 'lg' \| 'xl'` | `'ml'` | Tamanho |
| value | `number` | `0` | Valor controlado |
| onValueChange | `(value: number) => void` | - | Handler de mudança |
| disabled | `boolean` | `false` | Desabilitado |
| readOnly | `boolean` | `false` | Somente leitura |
| hasError | `boolean` | `false` | Estado de erro |

#### Exemplo de Uso

```tsx
<InputCounter.Root 
  size="ml" 
  value={quantidade}
  onValueChange={setQuantidade}
>
  <InputCounter.Label>Quantidade</InputCounter.Label>
  <InputCounter.Control>
    <InputCounter.Decrement />
    <InputCounter.Input />
    <InputCounter.Increment />
  </InputCounter.Control>
</InputCounter.Root>
```

---

### SearchBar

Barra de busca com botão de limpar.

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'md' \| 'ml' \| 'lg'` | `'md'` | Tamanho |
| value | `string` | `''` | Valor do campo |
| placeholder | `string` | - | Texto placeholder |
| onChange | `(e: ChangeEvent) => void` | - | Handler de mudança |
| handleSearch | `() => void` | - | Handler do botão buscar |
| handleClear | `() => void` | - | Handler do botão limpar |

#### Exemplo de Uso

```tsx
import { SearchBar } from '@rdsaude/pulso-react-components'

<SearchBar.Root 
  size="ml"
  value={searchValue}
  placeholder="Buscar medicamentos"
  onChange={(e) => setSearchValue(e.target.value)}
  handleSearch={() => doSearch()}
  handleClear={() => setSearchValue('')}
/>
```

---

### Chips

Componente de seleção em formato de chip.

#### Estrutura de Composição

```tsx
import { Chips } from '@rdsaude/pulso-react-components'

// Chips.Root - Container principal
// Chips.Single - Chip de seleção única (radio-like)
// Chips.Multiple - Chip de seleção múltipla
// Chips.Label - Rótulo do chip
// Chips.Input - Input invisível
```

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'sm' \| 'md' \| 'ml'` | `'md'` | Tamanho |
| disabled | `boolean` | `false` | Desabilitado |
| checked | `boolean` | `false` | Selecionado |

#### Exemplo de Uso

```tsx
// Chip Single (como radio)
<Chips.Root size="ml">
  <Chips.Single id="cat1" name="categoria" value="medicamentos" checked={selected === 'medicamentos'} onChange={() => setSelected('medicamentos')}>
    <Chips.Label>Medicamentos</Chips.Label>
  </Chips.Single>
  <Chips.Single id="cat2" name="categoria" value="beleza" checked={selected === 'beleza'} onChange={() => setSelected('beleza')}>
    <Chips.Label>Beleza</Chips.Label>
  </Chips.Single>
</Chips.Root>

// Chip Multiple (com contador)
<Chips.Root size="ml">
  <Chips.Multiple count={3}>
    <Chips.Label>Filtros</Chips.Label>
  </Chips.Multiple>
</Chips.Root>
```

---

## Componentes de Feedback

### Toast

Notificação temporária.

#### Estrutura de Composição

```tsx
import { Toast } from '@rdsaude/pulso-react-components'

// Toast.Root - Container principal
// Toast.Icon - Ícone do toast
// Toast.Description - Texto do toast
```

#### Toast.Root Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| type | `'neutral' \| 'informative' \| 'success' \| 'warning' \| 'danger'` | - | Tipo visual |

#### Exemplo de Uso

```tsx
<Toast.Root type="success">
  <Toast.Icon />
  <Toast.Description>Produto adicionado ao carrinho!</Toast.Description>
</Toast.Root>

<Toast.Root type="danger">
  <Toast.Icon />
  <Toast.Description>Erro ao processar pagamento</Toast.Description>
</Toast.Root>

<Toast.Root type="warning">
  <Toast.Icon />
  <Toast.Description>Estoque baixo</Toast.Description>
</Toast.Root>
```

---

### Snackbar

Notificação com ação opcional.

#### Estrutura de Composição

```tsx
import { Snackbar } from '@rdsaude/pulso-react-components'

// Snackbar.Root - Container principal
// Snackbar.Content - Conteúdo
// Snackbar.Footer - Área de ação
// Snackbar.Timebar - Barra de progresso temporal
```

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| type | `'brand-accent' \| 'informative' \| 'success' \| 'warning' \| 'danger'` | - | Tipo visual |
| layout | `'with-button' \| 'with-link'` | - | Layout com ação |
| duration | `number` | - | Duração em ms |
| buttonLabel | `string` | - | Texto do botão |
| onClickFooter | `() => void` | - | Handler do botão |

#### Exemplo de Uso

```tsx
<Snackbar.Root 
  type="success" 
  layout="with-button"
  buttonLabel="Desfazer"
  onClickFooter={() => undoAction()}
  duration={5000}
>
  <Snackbar.Content>Item removido do carrinho</Snackbar.Content>
  <Snackbar.Footer />
  <Snackbar.Timebar />
</Snackbar.Root>
```

---

### CardInformative

Card para exibir informações com destaque.

#### Estrutura de Composição

```tsx
import { CardInformative } from '@rdsaude/pulso-react-components'

// CardInformative.Root - Container principal
// CardInformative.Content - Área de conteúdo
// CardInformative.Title - Título
// CardInformative.Description - Descrição
```

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| type | `'highlight' \| 'icon' \| 'text'` | - | Tipo de exibição |
| variants | `'neutral' \| 'positive' \| 'informative' \| 'warning' \| 'negative'` | - | Variante visual |
| iconName | `IconName` | - | Ícone (para type icon/highlight) |

#### Exemplos de Uso

```tsx
// Card informativo positivo
<CardInformative.Root type="icon" variants="positive" iconName="rdicon-check-circle">
  <CardInformative.Content>
    <CardInformative.Title>Pedido confirmado!</CardInformative.Title>
    <CardInformative.Description>
      Seu pedido foi processado com sucesso.
    </CardInformative.Description>
  </CardInformative.Content>
</CardInformative.Root>

// Card de aviso
<CardInformative.Root type="highlight" variants="warning" iconName="rdicon-warning">
  <CardInformative.Content>
    <CardInformative.Title>Atenção</CardInformative.Title>
    <CardInformative.Description>
      Este medicamento requer receita médica.
    </CardInformative.Description>
  </CardInformative.Content>
</CardInformative.Root>

// Card de erro
<CardInformative.Root type="icon" variants="negative" iconName="rdicon-error">
  <CardInformative.Content>
    <CardInformative.Title>Erro no pagamento</CardInformative.Title>
    <CardInformative.Description>
      Verifique os dados do cartão e tente novamente.
    </CardInformative.Description>
  </CardInformative.Content>
</CardInformative.Root>
```

---

### ProgressIndicator

Indicador de progresso em barra.

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| variant | `'brand' \| 'neutral' \| 'informative' \| 'success' \| 'warning' \| 'danger'` | `'brand'` | Cor |
| size | `'tiny' \| 'mini' \| 'micro' \| 'nano' \| 'pico'` | `'tiny'` | Altura |
| percentage | `number` | `0` | Progresso (0-100) |
| duration | `number` | `0` | Animação automática em ms |
| bgTransparent | `boolean` | `false` | Fundo transparente |
| onComplete | `() => void` | - | Callback ao completar |

#### Exemplo de Uso

```tsx
import { ProgressIndicator } from '@rdsaude/pulso-react-components'

// Progresso estático
<ProgressIndicator 
  variant="brand"
  size="tiny"
  percentage={75}
  aria-labelledby="download-progress"
/>

// Progresso animado
<ProgressIndicator 
  variant="success"
  size="mini"
  duration={3000}
  onComplete={() => console.log('Concluído!')}
  aria-labelledby="loading-bar"
/>
```

---

### Stepper

Indicador de etapas/passos.

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| steps | `1-7` | - | Total de passos |
| completed | `number` | `0` | Passos completados |
| size | `'nano' \| 'pico'` | `'nano'` | Tamanho |
| label | `boolean` | `false` | Mostrar "Passo X de Y" |

#### Exemplo de Uso

```tsx
import { Stepper } from '@rdsaude/pulso-react-components'

<Stepper 
  steps={4}
  completed={2}
  label
/>
// Exibe: "Passo 2 de 4" com barras de progresso
```

---

### Rating

Componente de avaliação com estrelas.

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'tiny' \| 'small'` | `'tiny'` | Tamanho |
| value | `number` | - | Valor da avaliação |
| ratingLimit | `number` | `5` | Número de estrelas |
| onClick | `(value: number) => void` | - | Handler de clique |

#### Exemplo de Uso

```tsx
import { Rating } from '@rdsaude/pulso-react-components'

// Avaliação interativa
<Rating 
  size="small"
  value={rating}
  onClick={(value) => setRating(value)}
/>

// Avaliação com meia estrela
<Rating 
  size="tiny"
  value={4.5}
  onClick={() => {}}
/>
```

---

## Componentes de Navegação

### Link

Componente de link estilizado.

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'md' \| 'ml'` | `'md'` | Tamanho |
| icon | `boolean` | `false` | Exibir ícone de seta |
| disabled | `boolean` | `false` | Desabilitado |
| full | `boolean` | `false` | Largura total |
| href | `string` | - | URL de destino |

#### Exemplo de Uso

```tsx
import { Link } from '@rdsaude/pulso-react-components'

<Link.Root href="/produtos" size="ml" icon>
  Ver todos os produtos
</Link.Root>

<Link.Root href="/ajuda" size="md">
  Central de ajuda
</Link.Root>
```

---

### Pagination

Navegação entre páginas.

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| current | `number` | - | Página atual |
| total | `number` | - | Total de páginas |
| pagesMapper | `PageMapper[]` | - | Mapeamento de páginas |
| onPageClick | `(index: number) => void` | - | Handler de clique |
| prevControl | `PaginationControl` | - | Controle anterior |
| nextControl | `PaginationControl` | - | Controle próximo |

#### Exemplo de Uso

```tsx
import { Pagination } from '@rdsaude/pulso-react-components'

const pagesMapper = [
  { href: '/page/1' },
  { href: '/page/2' },
  { href: '/page/3' },
  { href: '/page/4' },
  { href: '/page/5' },
]

<Pagination
  current={2}
  total={5}
  pagesMapper={pagesMapper}
  onPageClick={(page) => setCurrentPage(page)}
  prevControl={{ href: '/page/1', onClickEvent: () => goToPrev() }}
  nextControl={{ href: '/page/3', onClickEvent: () => goToNext() }}
/>
```

---

### ListItem

Item de lista navegável.

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| title | `string` | - | Título principal |
| titleAs | `keyof JSX.IntrinsicElements` | `'h3'` | Elemento do título |
| description | `string` | - | Descrição secundária |
| disabled | `boolean` | `false` | Desabilitado |
| tag | `{ variant, label }` | - | Tag de status |
| leftIcon | `IconName` | - | Ícone à esquerda |
| showSeparator | `boolean` | `false` | Exibir separador |
| asChild | `boolean` | `false` | Renderizar como slot |
| href | `string` | - | URL de destino |

#### Exemplo de Uso

```tsx
import { ListItem } from '@rdsaude/pulso-react-components'

<ul>
  <ListItem
    title="Meus pedidos"
    description="Acompanhe suas compras"
    leftIcon="rdicon-package"
    showSeparator
    href="/pedidos"
  />
  <ListItem
    title="Meus endereços"
    description="Gerencie seus endereços"
    leftIcon="rdicon-location"
    tag={{ variant: 'principal', label: 'Novo' }}
    showSeparator
    href="/enderecos"
  />
  <ListItem
    title="Clube de descontos"
    description="Indisponível no momento"
    leftIcon="rdicon-star"
    disabled
  />
</ul>
```

---

## Componentes de Exibição

### Tag

Etiqueta de categorização.

#### Estrutura de Composição

```tsx
import { Tag } from '@rdsaude/pulso-react-components'

// Tag.Root - Container principal
// Tag.Label - Texto da tag
// Tag.Icon - Ícone opcional
```

#### Variantes Disponíveis

- `onSale` - Promoção
- `principal` - Destaque principal
- `secondary` - Destaque secundário
- `clubeRaia` - Clube Raia
- `clubeDrogasil` - Clube Drogasil
- `assinatura` - Assinatura
- `medicamentoGeladeira` - Medicamento refrigerado
- `receitaObrigatoria` - Receita obrigatória
- `generico` - Medicamento genérico
- `referencia` - Medicamento referência
- `similar` - Medicamento similar
- `stix` - Stix

#### Exemplo de Uso

```tsx
<Tag.Root variants="onSale">
  <Tag.Label>20% OFF</Tag.Label>
</Tag.Root>

<Tag.Root variants="generico">
  <Tag.Label>Genérico</Tag.Label>
</Tag.Root>

<Tag.Root variants="receitaObrigatoria">
  <Tag.Icon symbol="rdicon-prescription" />
  <Tag.Label>Receita obrigatória</Tag.Label>
</Tag.Root>
```

---

### Icon

Ícone do design system.

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| symbol | `IconName` | `'rdicon-default'` | Nome do ícone |
| size | `'tiny' \| 'extra-small' \| 'small' \| 'medium'` | `'small'` | Tamanho |
| color | `TokenColorKey` | `'colorActionFillBrandPrimaryEnabled'` | Cor (token) |

#### Ícones Comuns

- `rdicon-search` - Busca
- `rdicon-cart` - Carrinho
- `rdicon-user` - Usuário
- `rdicon-heart` - Favorito
- `rdicon-location` - Localização
- `rdicon-chevron-right` - Seta direita
- `rdicon-chevron-down` - Seta baixo
- `rdicon-check` - Check
- `rdicon-dismiss` - Fechar
- `rdicon-warning-circle` - Alerta
- `rdicon-star-filled` - Estrela preenchida
- `rdicon-star-outline` - Estrela vazia

#### Exemplo de Uso

```tsx
import { Icon } from '@rdsaude/pulso-react-components'

<Icon symbol="rdicon-cart" size="medium" color="colorActionFillBrandPrimaryEnabled" />
<Icon symbol="rdicon-heart" size="small" color="colorTextDangerAlternative" />
```

---

### Logo

Logotipos das marcas.

#### Variantes de Logo

**Pulso:**
- `Logo.PulsoColored` / `Logo.PulsoWhite` / `Logo.PulsoBlack`
- `Logo.PulsoIconColored` / `Logo.PulsoIconWhite` / `Logo.PulsoIconBlack`

**Raia:**
- `Logo.RaiaColored` / `Logo.RaiaWhite` / `Logo.RaiaBlack`
- `Logo.RaiaIconColored` / `Logo.RaiaIconWhite` / `Logo.RaiaIconBlack`

**Drogasil:**
- `Logo.DrogasilColored` / `Logo.DrogasilWhite` / `Logo.DrogasilBlack`
- `Logo.DrogasilIconColored` / `Logo.DrogasilIconWhite` / `Logo.DrogasilIconBlack`

**RD Saúde:**
- `Logo.RdSaudeColored` / `Logo.RdSaudeWhite` / `Logo.RdSaudeBlack`
- `Logo.RdSaudeTaglineColored` / `Logo.RdSaudeTaglineWhite`

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| size | `'large' \| 'huge' \| 'enormous'` | `'large'` | Tamanho |

#### Exemplo de Uso

```tsx
import { Logo } from '@rdsaude/pulso-react-components'

<Logo.RaiaColored size="large" />
<Logo.DrogasilColored size="huge" />
<Logo.PulsoIconWhite size="large" />
```

---

### ProductCard

Card de exibição de produto.

#### Estrutura de Composição

```tsx
import { ProductCard } from '@rdsaude/pulso-react-components'

// ProductCard.Root - Container principal
// ProductCard.Image - Imagem do produto
// ProductCard.Info - Informações do produto
// ProductCard.Price - Preço
// ProductCard.Action - Botão de ação
// ProductCard.Rating - Avaliação
// ProductCard.Shipping - Informação de frete
// ProductCard.Trade - Informação de troca
// ProductCard.Validate - Validade
```

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| variantCard | `string` | - | Variante do card |
| sponsored | `boolean` | - | É patrocinado |
| onSale | `boolean` | - | Em promoção |
| subscriptionText | `string` | - | Texto de assinatura |
| handleClick | `() => void` | - | Handler de clique |

#### Exemplo de Uso

```tsx
<ProductCard.Root 
  variantCard="default"
  onSale
  handleClick={() => goToProduct()}
>
  <ProductCard.Image src="/produto.jpg" alt="Nome do Produto" />
  <ProductCard.Info>
    <ProductCard.Rating value={4.5} />
    <Typography.Body>Nome do Medicamento 500mg</Typography.Body>
  </ProductCard.Info>
  <ProductCard.Price>
    <Typography.Body variant="default-regular">R$ 29,90</Typography.Body>
  </ProductCard.Price>
  <ProductCard.Action>
    <Button.Root variant="brand-primary" full>
      Adicionar
    </Button.Root>
  </ProductCard.Action>
</ProductCard.Root>
```

---

## Componentes de Overlay

### Modal

Caixa de diálogo modal.

#### Estrutura de Composição

```tsx
import { Modal } from '@rdsaude/pulso-react-components'

// Modal.Root - Container principal
// Modal.HeaderIcon - Ícone do header
// Modal.HeaderTitle - Título
// Modal.HeaderClosableButton - Botão fechar
// Modal.Description - Descrição
// Modal.Body - Corpo do modal
// Modal.Footer - Rodapé
// Modal.PrimaryButton - Botão primário
// Modal.SecondaryButton - Botão secundário
```

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| variant | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Tamanho |
| visible | `boolean` | `false` | Visibilidade |

#### Exemplo de Uso

```tsx
<Modal.Root variant="md" visible={isOpen}>
  <Modal.HeaderIcon symbol="rdicon-warning" />
  <Modal.HeaderTitle>Confirmar exclusão</Modal.HeaderTitle>
  <Modal.HeaderClosableButton onClick={() => setIsOpen(false)} />
  
  <Modal.Description>
    Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.
  </Modal.Description>
  
  <Modal.Footer>
    <Modal.SecondaryButton onClick={() => setIsOpen(false)}>
      Cancelar
    </Modal.SecondaryButton>
    <Modal.PrimaryButton onClick={handleDelete}>
      Excluir
    </Modal.PrimaryButton>
  </Modal.Footer>
</Modal.Root>
```

---

### SideSheet

Painel lateral deslizante.

#### Estrutura de Composição

```tsx
import { SideSheet } from '@rdsaude/pulso-react-components'

// SideSheet.Root - Container principal
// SideSheet.Trigger - Elemento que abre
// SideSheet.Content - Conteúdo
// SideSheet.Header - Cabeçalho
// SideSheet.Close - Botão fechar
```

#### Exemplo de Uso

```tsx
<SideSheet.Root>
  <SideSheet.Trigger>
    <Button.Root variant="neutral-secondary">
      Abrir Menu
    </Button.Root>
  </SideSheet.Trigger>
  
  <SideSheet.Content>
    <SideSheet.Header>
      <Typography.Title variant="default-bold">Menu</Typography.Title>
      <SideSheet.Close>
        <Button.Root variant="neutral-tertiary">
          <Button.Icon symbol="rdicon-dismiss" />
        </Button.Root>
      </SideSheet.Close>
    </SideSheet.Header>
    
    {/* Conteúdo do menu */}
    <nav>
      <ListItem title="Home" href="/" />
      <ListItem title="Produtos" href="/produtos" />
      <ListItem title="Contato" href="/contato" />
    </nav>
  </SideSheet.Content>
</SideSheet.Root>
```

---

### BottomSheet

Painel inferior deslizante (mobile).

#### Estrutura de Composição

```tsx
import { BottomSheet } from '@rdsaude/pulso-react-components'

// BottomSheet.Root - Container principal
// BottomSheet.Trigger - Elemento que abre
// BottomSheet.Content - Conteúdo
// BottomSheet.Header - Cabeçalho
// BottomSheet.Close - Botão fechar
```

#### Exemplo de Uso

```tsx
<BottomSheet.Root>
  <BottomSheet.Trigger>
    <Button.Root variant="neutral-secondary">
      Filtros
    </Button.Root>
  </BottomSheet.Trigger>
  
  <BottomSheet.Content>
    <BottomSheet.Header>
      <Typography.Title variant="default-bold">Filtros</Typography.Title>
      <BottomSheet.Close>
        <Button.Root variant="neutral-tertiary">
          <Button.Icon symbol="rdicon-dismiss" />
        </Button.Root>
      </BottomSheet.Close>
    </BottomSheet.Header>
    
    {/* Conteúdo dos filtros */}
  </BottomSheet.Content>
</BottomSheet.Root>
```

---

### Tooltip

Dica de contexto ao passar o mouse.

#### Estrutura de Composição

```tsx
import { Tooltip } from '@rdsaude/pulso-react-components'

// Tooltip.Root - Container principal
// Tooltip.Trigger - Elemento que ativa
// Tooltip.Content - Conteúdo do tooltip
```

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| side | `'top' \| 'bottom' \| 'left' \| 'right'` | `'bottom'` | Posição |
| distance | `TokenSpacingKey` | `'spacingStackTwopulse'` | Distância |
| disabled | `boolean` | `false` | Desabilitado |

#### Exemplo de Uso

```tsx
<Tooltip.Root side="top">
  <Tooltip.Trigger>
    <Button.Root variant="neutral-tertiary">
      <Button.Icon symbol="rdicon-info" />
    </Button.Root>
  </Tooltip.Trigger>
  <Tooltip.Content>
    Este medicamento requer receita médica
  </Tooltip.Content>
</Tooltip.Root>
```

---

### Popover

Pop-up de conteúdo rico.

#### Estrutura de Composição

```tsx
import { Popover } from '@rdsaude/pulso-react-components'

// Popover.Root - Container principal
// Popover.Trigger - Elemento que abre (passado como prop)
// Popover.Title - Título
// Popover.Tag - Tag opcional
// Popover.Description - Descrição
// Popover.Button - Botão de ação
```

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| placement | `PlacementType` | `'bottom-start'` | Posição |
| trigger | `ReactNode` | - | Elemento trigger |
| hasButtonClose | `boolean` | `false` | Mostrar botão fechar |
| handleClickButtonClose | `() => void` | - | Handler do botão fechar |
| open | `boolean` | - | Estado controlado |

#### Exemplo de Uso

```tsx
<Popover.Root
  placement="bottom-start"
  trigger={
    <Button.Root variant="neutral-tertiary">
      <Button.Icon symbol="rdicon-info" />
    </Button.Root>
  }
  hasButtonClose
>
  <Popover.Title>Informações do Produto</Popover.Title>
  <Popover.Description>
    Este medicamento é indicado para dores de cabeça e febre.
  </Popover.Description>
  <Popover.Button>Ver bula completa</Popover.Button>
</Popover.Root>
```

---

### Accordion

Seção expansível.

#### Props

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| title | `string` | - | Título do accordion |
| disabled | `boolean` | `false` | Desabilitado |

#### Exemplo de Uso

```tsx
import { Accordion } from '@rdsaude/pulso-react-components'

<Accordion.Root title="Informações do Produto">
  <Typography.Body variant="default-regular">
    Este medicamento é indicado para o alívio de dores de cabeça, 
    dores musculares e febre.
  </Typography.Body>
</Accordion.Root>

<Accordion.Root title="Modo de Usar">
  <Typography.Body variant="default-regular">
    Tomar 1 comprimido de 6 em 6 horas.
  </Typography.Body>
</Accordion.Root>
```

---

## Templates de Páginas


---

### Template: Página de Produto (PDP)

```tsx
import { 
  ThemeProvider, 
  Button, 
  InputCounter, 
  Typography, 
  Tag,
  Rating,
  Accordion,
  Toast,
  CardInformative,
  Breadcrumb
} from '@rdsaude/pulso-react-components'

function ProductDetailPage({ product }) {
  const [quantity, setQuantity] = useState(1)
  const [showToast, setShowToast] = useState(false)

  const handleAddToCart = () => {
    // Adicionar ao carrinho
    setShowToast(true)
    setTimeout(() => setShowToast(false), 3000)
  }

  return (
    <ThemeProvider theme="drogasil">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Toast de sucesso */}
        {showToast && (
          <div className="fixed top-4 right-4 z-50">
            <Toast.Root type="success">
              <Toast.Icon />
              <Toast.Description>Produto adicionado ao carrinho!</Toast.Description>
            </Toast.Root>
          </div>
        )}

        {/* Grid do produto */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Coluna da imagem */}
          <div className="space-y-4">
            <img 
              src={product.image} 
              alt={product.name}
              className="w-full rounded-lg"
            />
          </div>

          {/* Coluna de informações */}
          <div className="space-y-6">
            {/* Tags */}
            <div className="flex gap-2">
              {product.isGeneric && (
                <Tag.Root variants="generico">
                  <Tag.Label>Genérico</Tag.Label>
                </Tag.Root>
              )}
              {product.onSale && (
                <Tag.Root variants="onSale">
                  <Tag.Label>-{product.discount}%</Tag.Label>
                </Tag.Root>
              )}
              {product.requiresPrescription && (
                <Tag.Root variants="receitaObrigatoria">
                  <Tag.Label>Receita obrigatória</Tag.Label>
                </Tag.Root>
              )}
            </div>

            {/* Nome e Avaliação */}
            <div>
              <Typography.Title variant="large-bold">
                {product.name}
              </Typography.Title>
              <Typography.Body variant="default-regular">
                {product.brand} | {product.presentation}
              </Typography.Body>
              <div className="flex items-center gap-2 mt-2">
                <Rating size="tiny" value={product.rating} onClick={() => {}} />
                <Typography.Caption>
                  ({product.reviewCount} avaliações)
                </Typography.Caption>
              </div>
            </div>

            {/* Preço */}
            <div className="space-y-1">
              {product.oldPrice && (
                <Typography.Body variant="default-regular" className="line-through text-gray-400">
                  R$ {product.oldPrice.toFixed(2)}
                </Typography.Body>
              )}
              <Typography.BigNumber>
                R$ {product.price.toFixed(2)}
              </Typography.BigNumber>
              <Typography.Caption>
                ou 3x de R$ {(product.price / 3).toFixed(2)} sem juros
              </Typography.Caption>
            </div>

            {/* Aviso de receita */}
            {product.requiresPrescription && (
              <CardInformative.Root type="highlight" variants="warning" iconName="rdicon-prescription">
                <CardInformative.Content>
                  <CardInformative.Title>Medicamento controlado</CardInformative.Title>
                  <CardInformative.Description>
                    Este medicamento exige apresentação de receita médica no momento da entrega.
                  </CardInformative.Description>
                </CardInformative.Content>
              </CardInformative.Root>
            )}

            {/* Quantidade e Comprar */}
            <div className="flex gap-4 items-end">
              <InputCounter.Root 
                size="lg" 
                value={quantity}
                onValueChange={setQuantity}
              >
                <InputCounter.Label>Quantidade</InputCounter.Label>
                <InputCounter.Control>
                  <InputCounter.Decrement />
                  <InputCounter.Input />
                  <InputCounter.Increment />
                </InputCounter.Control>
              </InputCounter.Root>

              <div className="flex-1">
                <Button.Root variant="brand-primary" full onClick={handleAddToCart}>
                  <Button.Icon symbol="rdicon-cart" />
                  Adicionar ao Carrinho
                </Button.Root>
              </div>
            </div>

            {/* Frete */}
            <div className="p-4 border rounded-lg">
              <Typography.Subtitle>Calcular frete</Typography.Subtitle>
              <div className="flex gap-2 mt-2">
                <InputText.Root size="ml">
                  <InputText.Actions>
                    <InputText.Field placeholder="Digite seu CEP" />
                  </InputText.Actions>
                </InputText.Root>
                <Button.Root variant="neutral-secondary">
                  Calcular
                </Button.Root>
              </div>
            </div>
          </div>
        </div>

        {/* Detalhes do produto */}
        <div className="mt-12 space-y-4">
          <Typography.Title variant="default-bold">
            Detalhes do Produto
          </Typography.Title>

          <Accordion.Root title="Descrição">
            <Typography.Body variant="default-regular">
              {product.description}
            </Typography.Body>
          </Accordion.Root>

          <Accordion.Root title="Indicação">
            <Typography.Body variant="default-regular">
              {product.indication}
            </Typography.Body>
          </Accordion.Root>

          <Accordion.Root title="Modo de Usar">
            <Typography.Body variant="default-regular">
              {product.howToUse}
            </Typography.Body>
          </Accordion.Root>

          <Accordion.Root title="Composição">
            <Typography.Body variant="default-regular">
              {product.composition}
            </Typography.Body>
          </Accordion.Root>

          <Accordion.Root title="Contraindicações">
            <Typography.Body variant="default-regular">
              {product.contraindications}
            </Typography.Body>
          </Accordion.Root>
        </div>
      </div>
    </ThemeProvider>
  )
}
```


---

## Ícones Disponíveis (rdicon-*)

A biblioteca `@raiadrogasil/pulso-icons` contém mais de 300 ícones. Abaixo está a lista completa organizada por categoria.

### Navegação e Setas

| Ícone | Descrição |
|-------|-----------|
| `rdicon-chevron-down` | Seta para baixo |
| `rdicon-chevron-left` | Seta para esquerda |
| `rdicon-chevron-right` | Seta para direita |
| `rdicon-chevron-up` | Seta para cima |
| `rdicon-arrow-down` | Flecha para baixo |
| `rdicon-arrow-left` | Flecha para esquerda |
| `rdicon-arrow-right` | Flecha para direita |
| `rdicon-arrow-up` | Flecha para cima |
| `rdicon-arrow-right-circle` | Flecha direita com círculo |
| `rdicon-arrow-right-circle-filled` | Flecha direita com círculo preenchido |
| `rdicon-arrow-download` | Download |
| `rdicon-change-vertical` | Troca vertical |
| `rdicon-change-horizontal` | Troca horizontal |
| `rdicon-expand` | Expandir |
| `rdicon-contract` | Contrair |
| `rdicon-expand-vertical` | Expandir vertical |
| `rdicon-expand-horizontal` | Expandir horizontal |
| `rdicon-near-me` | Perto de mim |
| `rdicon-near-me-filled` | Perto de mim preenchido |

### Ações Gerais

| Ícone | Descrição |
|-------|-----------|
| `rdicon-menu` | Menu hamburguer |
| `rdicon-search` | Busca |
| `rdicon-plus` | Adicionar |
| `rdicon-minus` | Remover |
| `rdicon-dismiss` | Fechar (X) |
| `rdicon-dismiss-circle-outline` | Fechar com círculo outline |
| `rdicon-dismiss-circle-filled` | Fechar com círculo preenchido |
| `rdicon-checkmark` | Confirmação |
| `rdicon-checkmark-circle` | Confirmação com círculo |
| `rdicon-checkmark-circle-filled` | Confirmação com círculo preenchido |
| `rdicon-edit` | Editar |
| `rdicon-edit-filled` | Editar preenchido |
| `rdicon-delete` | Excluir |
| `rdicon-delete-filled` | Excluir preenchido |
| `rdicon-copy` | Copiar |
| `rdicon-copy-filled` | Copiar preenchido |
| `rdicon-save` | Salvar |
| `rdicon-save-filled` | Salvar preenchido |
| `rdicon-share` | Compartilhar |
| `rdicon-send-outline` | Enviar outline |
| `rdicon-send-filled` | Enviar preenchido |
| `rdicon-print` | Imprimir |
| `rdicon-print-filled` | Imprimir preenchido |
| `rdicon-attach` | Anexar |
| `rdicon-link` | Link |
| `rdicon-open` | Abrir externa |
| `rdicon-refresh` | Atualizar |
| `rdicon-reload` | Recarregar |
| `rdicon-settings` | Configurações |
| `rdicon-options-filter` | Filtrar opções |
| `rdicon-options-filter-filled` | Filtrar opções preenchido |
| `rdicon-filter` | Filtro |
| `rdicon-filter-filled` | Filtro preenchido |
| `rdicon-blocked` | Bloqueado |
| `rdicon-sign-in` | Entrar |
| `rdicon-sign-out` | Sair |
| `rdicon-history` | Histórico |
| `rdicon-archived` | Arquivado |
| `rdicon-archived-filled` | Arquivado preenchido |

### Visualização

| Ícone | Descrição |
|-------|-----------|
| `rdicon-eye` | Visualizar |
| `rdicon-eye-filled` | Visualizar preenchido |
| `rdicon-eye-off` | Ocultar |
| `rdicon-view-grid` | Grade |
| `rdicon-view-grid-filled` | Grade preenchido |
| `rdicon-view-list` | Lista |
| `rdicon-view-list-filled` | Lista preenchido |
| `rdicon-view-dashboard` | Dashboard |
| `rdicon-view-dashboard-filled` | Dashboard preenchido |
| `rdicon-more-horizontal` | Mais horizontal |
| `rdicon-more-vertical` | Mais vertical |
| `rdicon-order-ascending` | Ordem ascendente |
| `rdicon-order-descending` | Ordem descendente |
| `rdicon-order-alphabetical-ascending` | Ordem A-Z |
| `rdicon-order-alphabetical-descending` | Ordem Z-A |
| `rdicon-image` | Imagem |
| `rdicon-image-filled` | Imagem preenchido |
| `rdicon-camera` | Câmera |
| `rdicon-camera-filled` | Câmera preenchido |
| `rdicon-scan` | Escanear |
| `rdicon-qr-code` | QR Code |
| `rdicon-barcode` | Código de barras |
| `rdicon-barcode-scan` | Escanear código |
| `rdicon-barcode-scan-variant` | Escanear código variante |

### Usuário e Pessoas

| Ícone | Descrição |
|-------|-----------|
| `rdicon-person` | Pessoa |
| `rdicon-person-filled` | Pessoa preenchido |
| `rdicon-person-circle` | Pessoa círculo |
| `rdicon-person-circle-filled` | Pessoa círculo preenchido |
| `rdicon-person-id` | Documento pessoa |
| `rdicon-person-id-filled` | Documento pessoa preenchido |
| `rdicon-person-plus` | Adicionar pessoa |
| `rdicon-person-error` | Erro pessoa |
| `rdicon-person-warning` | Aviso pessoa |
| `rdicon-person-clock` | Pessoa com relógio |
| `rdicon-person-help` | Ajuda pessoa |
| `rdicon-person-pill` | Pessoa medicamento |
| `rdicon-people` | Pessoas |
| `rdicon-people-filled` | Pessoas preenchido |
| `rdicon-male-figure` | Figura masculina |
| `rdicon-baby` | Bebê |
| `rdicon-baby-filled` | Bebê preenchido |
| `rdicon-baby-pill` | Bebê medicamento |
| `rdicon-baby-pill-filled` | Bebê medicamento preenchido |
| `rdicon-company-badge` | Crachá empresa |
| `rdicon-company-badge-filled` | Crachá empresa preenchido |
| `rdicon-faceid` | Face ID |
| `rdicon-touchid` | Touch ID |

### Acessibilidade

| Ícone | Descrição |
|-------|-----------|
| `rdicon-accessibility` | Acessibilidade |
| `rdicon-accessibility-variant` | Acessibilidade variante |
| `rdicon-accessibility-circle` | Acessibilidade círculo |
| `rdicon-accessibility-circle-filled` | Acessibilidade círculo preenchido |
| `rdicon-accessibility-variant-circle` | Acessibilidade variante círculo |
| `rdicon-accessibility-variant-circle-filled` | Acessibilidade variante círculo preenchido |
| `rdicon-accessible` | Cadeira de rodas |
| `rdicon-accessible-forward` | Cadeira de rodas movimento |
| `rdicon-accessible-off` | Cadeira de rodas desativado |
| `rdicon-ear` | Orelha |
| `rdicon-ear-filled` | Orelha preenchido |
| `rdicon-ear-warning` | Orelha aviso |
| `rdicon-ear-checkmark` | Orelha confirmado |
| `rdicon-hearing-device` | Aparelho auditivo |
| `rdicon-hearing-device-filled` | Aparelho auditivo preenchido |
| `rdicon-hearing-device-off` | Aparelho auditivo desativado |
| `rdicon-magazine-braille` | Braille |
| `rdicon-magazine-braille-filled` | Braille preenchido |
| `rdicon-subtitles` | Legendas |
| `rdicon-subtitles-filled` | Legendas preenchido |
| `rdicon-subtitles-off` | Legendas desativado |

### Comunicação

| Ícone | Descrição |
|-------|-----------|
| `rdicon-mail` | E-mail |
| `rdicon-mail-filled` | E-mail preenchido |
| `rdicon-mail-read` | E-mail lido |
| `rdicon-mail-read-filled` | E-mail lido preenchido |
| `rdicon-mail-unread` | E-mail não lido |
| `rdicon-mail-unread-multicolor` | E-mail não lido multicolor |
| `rdicon-mail-unread-bullet-notification` | E-mail com notificação |
| `rdicon-mail-checkmark` | E-mail confirmado |
| `rdicon-mail-error` | E-mail erro |
| `rdicon-mail-warning` | E-mail aviso |
| `rdicon-mail-help` | E-mail ajuda |
| `rdicon-chat` | Chat |
| `rdicon-chat-filled` | Chat preenchido |
| `rdicon-chat-typing` | Chat digitando |
| `rdicon-chat-typing-filled` | Chat digitando preenchido |
| `rdicon-chat-help` | Chat ajuda |
| `rdicon-chat-help-filled` | Chat ajuda preenchido |
| `rdicon-chat-unread` | Chat não lido |
| `rdicon-chat-unread-multicolor` | Chat não lido multicolor |
| `rdicon-chat-unread-bullet-notification` | Chat com notificação |
| `rdicon-chat-multicolor` | Chat multicolor |
| `rdicon-chat-multicolor-plus` | Chat multicolor com mais |
| `rdicon-chat-notification-1` até `rdicon-chat-notification-9-plus` | Chat com contador |
| `rdicon-call` | Telefone |
| `rdicon-call-filled` | Telefone preenchido |
| `rdicon-headphone` | Fone de ouvido |
| `rdicon-headphone-filled` | Fone de ouvido preenchido |
| `rdicon-microphone` | Microfone |
| `rdicon-microphone-filled` | Microfone preenchido |
| `rdicon-video` | Vídeo |
| `rdicon-video-filled` | Vídeo preenchido |
| `rdicon-video-person` | Vídeo chamada |
| `rdicon-video-person-filled` | Vídeo chamada preenchido |
| `rdicon-video-off` | Vídeo desativado |
| `rdicon-telesales` | Televendas |
| `rdicon-telesales-filled` | Televendas preenchido |

### Notificações

| Ícone | Descrição |
|-------|-----------|
| `rdicon-notification` | Notificação |
| `rdicon-notification-filled` | Notificação preenchido |
| `rdicon-notification-on` | Notificação ativa |
| `rdicon-notification-on-filled` | Notificação ativa preenchido |
| `rdicon-notification-off` | Notificação desativada |
| `rdicon-notification-snooze` | Notificação soneca |
| `rdicon-notification-error` | Notificação erro |
| `rdicon-notification-1` até `rdicon-notification-9-plus` | Notificação com contador |
| `rdicon-notification-multicolor` | Notificação multicolor |
| `rdicon-notification-multicolor-plus` | Notificação multicolor com mais |
| `rdicon-bullet-notification-1` até `rdicon-bullet-notification-9-plus` | Badge contador |

### Status e Feedback

| Ícone | Descrição |
|-------|-----------|
| `rdicon-info-circle` | Informação |
| `rdicon-info-circle-filled` | Informação preenchido |
| `rdicon-help-circle` | Ajuda |
| `rdicon-help-circle-filled` | Ajuda preenchido |
| `rdicon-warning` | Alerta |
| `rdicon-warning-filled` | Alerta preenchido |
| `rdicon-warning-circle` | Alerta círculo |
| `rdicon-warning-circle-filled` | Alerta círculo preenchido |
| `rdicon-verified-outline` | Verificado outline |
| `rdicon-verified-filled` | Verificado preenchido |
| `rdicon-shield` | Escudo |
| `rdicon-shield-filled` | Escudo preenchido |
| `rdicon-shield-checkmark` | Escudo confirmado |
| `rdicon-shield-error` | Escudo erro |
| `rdicon-shield-warning` | Escudo aviso |
| `rdicon-flag` | Bandeira |
| `rdicon-flag-filled` | Bandeira preenchido |
| `rdicon-signal` | Sinal |

### Emojis

| Ícone | Descrição |
|-------|-----------|
| `rdicon-emoji-smile` | Sorriso |
| `rdicon-emoji-smile-filled` | Sorriso preenchido |
| `rdicon-emoji-laugh` | Rindo |
| `rdicon-emoji-laugh-filled` | Rindo preenchido |
| `rdicon-emoji-meh` | Neutro |
| `rdicon-emoji-meh-filled` | Neutro preenchido |
| `rdicon-emoji-sad` | Triste |
| `rdicon-emoji-sad-filled` | Triste preenchido |
| `rdicon-emoji-angry` | Bravo |
| `rdicon-emoji-angry-filled` | Bravo preenchido |
| `rdicon-emoji-surprise` | Surpreso |
| `rdicon-emoji-surprise-filled` | Surpreso preenchido |
| `rdicon-thumb-like` | Like |
| `rdicon-thumb-like-filled` | Like preenchido |
| `rdicon-thumb-dislike` | Dislike |
| `rdicon-thumb-dislike-filled` | Dislike preenchido |

### Avaliação

| Ícone | Descrição |
|-------|-----------|
| `rdicon-star-filled` | Estrela preenchida |
| `rdicon-star-outline` | Estrela outline |
| `rdicon-star-half` | Meia estrela |
| `rdicon-star-plus` | Estrela com mais |
| `rdicon-medal` | Medalha |
| `rdicon-medal-filled` | Medalha preenchido |
| `rdicon-medal-variant` | Medalha variante |
| `rdicon-medal-variant-filled` | Medalha variante preenchido |

### E-commerce / Compras

| Ícone | Descrição |
|-------|-----------|
| `rdicon-basket` | Cesta |
| `rdicon-basket-filled` | Cesta preenchido |
| `rdicon-basket-plus` | Adicionar à cesta |
| `rdicon-basket-checkmark` | Cesta confirmada |
| `rdicon-basket-error` | Cesta erro |
| `rdicon-basket-warning` | Cesta aviso |
| `rdicon-basket-notification-1` até `rdicon-basket-notification-9-plus` | Cesta com contador |
| `rdicon-basket-multicolor` | Cesta multicolor |
| `rdicon-basket-multicolor-plus` | Cesta multicolor com mais |
| `rdicon-bag` | Sacola |
| `rdicon-bag-filled` | Sacola preenchido |
| `rdicon-trolley-cart` | Carrinho de compras |
| `rdicon-tag` | Etiqueta |
| `rdicon-tag-filled` | Etiqueta preenchido |
| `rdicon-tag-error` | Etiqueta erro |
| `rdicon-tag-warning` | Etiqueta aviso |
| `rdicon-tag-help` | Etiqueta ajuda |
| `rdicon-tag-plus` | Etiqueta mais |
| `rdicon-tag-percentage` | Etiqueta percentual |
| `rdicon-tag-10` até `rdicon-tag-90` | Etiquetas de desconto |
| `rdicon-ticket-discount` | Cupom desconto |
| `rdicon-ticket-discount-filled` | Cupom desconto preenchido |
| `rdicon-ticket` | Ticket |
| `rdicon-ticket-filled` | Ticket preenchido |
| `rdicon-ticket-confirmation` | Ticket confirmação |
| `rdicon-ticket-confirmation-filled` | Ticket confirmação preenchido |
| `rdicon-ticket-person` | Ticket pessoa |
| `rdicon-ticket-person-filled` | Ticket pessoa preenchido |
| `rdicon-ticket-star` | Ticket estrela |
| `rdicon-ticket-star-filled` | Ticket estrela preenchido |
| `rdicon-sale-outline` | Promoção outline |
| `rdicon-sale-filled` | Promoção preenchido |
| `rdicon-sale-variant` | Promoção variante |
| `rdicon-gift` | Presente |
| `rdicon-gift-filled` | Presente preenchido |
| `rdicon-gift-card` | Vale presente |
| `rdicon-gift-card-filled` | Vale presente preenchido |
| `rdicon-coin-outline` | Moeda outline |
| `rdicon-coin-filled` | Moeda preenchido |
| `rdicon-coin-transfer` | Transferência moeda |
| `rdicon-coin-stix` | Moeda Stix |
| `rdicon-coin-stix-filled` | Moeda Stix preenchido |

### Pagamentos

| Ícone | Descrição |
|-------|-----------|
| `rdicon-credit-card` | Cartão de crédito |
| `rdicon-credit-card-filled` | Cartão preenchido |
| `rdicon-credit-card-checkmark` | Cartão confirmado |
| `rdicon-credit-card-error` | Cartão erro |
| `rdicon-credit-card-warning` | Cartão aviso |
| `rdicon-credit-card-help` | Cartão ajuda |
| `rdicon-credit-card-plus` | Adicionar cartão |
| `rdicon-credit-card-return` | Cartão devolução |
| `rdicon-credit-card-machine` | Máquina de cartão |
| `rdicon-credit-card-clock` | Cartão com relógio |
| `rdicon-pix` | PIX |
| `rdicon-pix-filled` | PIX preenchido |
| `rdicon-bank` | Banco |
| `rdicon-bank-filled` | Banco preenchido |
| `rdicon-wallet` | Carteira |
| `rdicon-wallet-filled` | Carteira preenchido |
| `rdicon-wallet-variant` | Carteira variante |
| `rdicon-wallet-variant-filled` | Carteira variante preenchido |
| `rdicon-receipt` | Recibo |
| `rdicon-receipt-filled` | Recibo preenchido |
| `rdicon-receipt-checkmark` | Recibo confirmado |
| `rdicon-receipt-error` | Recibo erro |
| `rdicon-receipt-sale` | Recibo venda |
| `rdicon-receipt-clock` | Recibo com relógio |
| `rdicon-invoice` | Fatura |
| `rdicon-invoice-checkmark` | Fatura confirmada |
| `rdicon-invoice-error` | Fatura erro |

### Entrega e Logística

| Ícone | Descrição |
|-------|-----------|
| `rdicon-truck-delivery` | Caminhão entrega |
| `rdicon-truck-delivery-filled` | Caminhão preenchido |
| `rdicon-truck-delivery-checkmark` | Caminhão confirmado |
| `rdicon-truck-delivery-error` | Caminhão erro |
| `rdicon-truck-delivery-warning` | Caminhão aviso |
| `rdicon-truck-delivery-clock` | Caminhão com relógio |
| `rdicon-truck-delivery-fast` | Caminhão rápido |
| `rdicon-truck-delivery-help` | Caminhão ajuda |
| `rdicon-motorcycle-super-express-delivery` | Moto express |
| `rdicon-motorcycle-super-express-delivery-filled` | Moto express preenchido |
| `rdicon-rocket-delivery-turbo` | Entrega turbo |
| `rdicon-rocket-delivery-turbo-filled` | Entrega turbo preenchido |
| `rdicon-neighborhood-delivery` | Entrega vizinhança |
| `rdicon-buy-take-away` | Retirar na loja |
| `rdicon-box` | Caixa |
| `rdicon-box-filled` | Caixa preenchido |
| `rdicon-box-checkmark` | Caixa confirmada |
| `rdicon-box-error` | Caixa erro |
| `rdicon-box-warning` | Caixa aviso |
| `rdicon-box-clock` | Caixa com relógio |
| `rdicon-box-return` | Caixa devolução |
| `rdicon-box-help` | Caixa ajuda |
| `rdicon-box-multiple` | Caixas múltiplas |
| `rdicon-box-multiple-filled` | Caixas múltiplas preenchido |
| `rdicon-box-multiple-plus` | Caixas múltiplas mais |
| `rdicon-box-multiple-checkmark` | Caixas múltiplas confirmado |
| `rdicon-box-multiple-error` | Caixas múltiplas erro |
| `rdicon-box-multiple-warning` | Caixas múltiplas aviso |
| `rdicon-box-multiple-clock` | Caixas múltiplas relógio |
| `rdicon-box-multiple-return` | Caixas múltiplas devolução |
| `rdicon-box-multiple-location` | Caixas múltiplas localização |
| `rdicon-box-multiple-help` | Caixas múltiplas ajuda |
| `rdicon-box-multiple-refresh` | Caixas múltiplas atualizar |
| `rdicon-warehouse` | Armazém |
| `rdicon-warehouse-filled` | Armazém preenchido |
| `rdicon-warehouse-checkmark` | Armazém confirmado |
| `rdicon-warehouse-error` | Armazém erro |
| `rdicon-warehouse-warning` | Armazém aviso |
| `rdicon-warehouse-return` | Armazém devolução |

### Localização

| Ícone | Descrição |
|-------|-----------|
| `rdicon-location` | Localização |
| `rdicon-location-filled` | Localização preenchido |
| `rdicon-location-plus` | Adicionar localização |
| `rdicon-location-error` | Localização erro |
| `rdicon-location-off` | Localização desativada |
| `rdicon-location-parking` | Estacionamento |
| `rdicon-map` | Mapa |
| `rdicon-map-filled` | Mapa preenchido |
| `rdicon-map-variant` | Mapa variante |
| `rdicon-globe` | Globo |
| `rdicon-globe-filled` | Globo preenchido |
| `rdicon-store` | Loja |
| `rdicon-store-filled` | Loja preenchido |
| `rdicon-store-heart` | Loja favorita |
| `rdicon-store-checkmark` | Loja confirmada |
| `rdicon-store-error` | Loja erro |
| `rdicon-hospital` | Hospital |
| `rdicon-hospital-filled` | Hospital preenchido |

### Data e Tempo

| Ícone | Descrição |
|-------|-----------|
| `rdicon-clock` | Relógio |
| `rdicon-clock-filled` | Relógio preenchido |
| `rdicon-clock-plus` | Relógio mais |
| `rdicon-clock-error` | Relógio erro |
| `rdicon-clock-fast` | Relógio rápido |
| `rdicon-clock-pending` | Relógio pendente |
| `rdicon-clock-pill` | Relógio medicamento |
| `rdicon-hour-24` | 24 horas |
| `rdicon-hour-24-filled` | 24 horas preenchido |
| `rdicon-calendar-empty` | Calendário vazio |
| `rdicon-calendar-empty-filled` | Calendário vazio preenchido |
| `rdicon-calendar-month` | Calendário mês |
| `rdicon-calendar-month-filled` | Calendário mês preenchido |
| `rdicon-calendar-period` | Calendário período |
| `rdicon-calendar-period-filled` | Calendário período preenchido |
| `rdicon-calendar-clock` | Calendário com relógio |
| `rdicon-calendar-edit` | Calendário editar |
| `rdicon-calendar-box` | Calendário caixa |
| `rdicon-calendar-pause` | Calendário pausado |
| `rdicon-calendar-location` | Calendário localização |
| `rdicon-calendar-help` | Calendário ajuda |
| `rdicon-watch` | Relógio de pulso |

### Saúde e Medicamentos

| Ícone | Descrição |
|-------|-----------|
| `rdicon-pill` | Pílula |
| `rdicon-pill-filled` | Pílula preenchido |
| `rdicon-pill-variant` | Pílula variante |
| `rdicon-round-pill` | Pílula redonda |
| `rdicon-medicine-bottle` | Frasco de medicamento |
| `rdicon-vitamins-bottle` | Frasco de vitaminas |
| `rdicon-vitamins-bottle-filled` | Frasco vitaminas preenchido |
| `rdicon-prescription` | Receita médica |
| `rdicon-prescription-search` | Buscar receita |
| `rdicon-prescribing-information` | Bula |
| `rdicon-document-prescription` | Documento receita |
| `rdicon-digital-prescription` | Receita digital |
| `rdicon-syringe` | Seringa |
| `rdicon-bandage` | Curativo |
| `rdicon-bandage-filled` | Curativo preenchido |
| `rdicon-bandage-variant` | Curativo variante |
| `rdicon-bandage-variant-filled` | Curativo variante preenchido |
| `rdicon-thermometer-digital` | Termômetro digital |
| `rdicon-thermometer-mercury` | Termômetro mercúrio |
| `rdicon-thermostat-minimum` | Termostato mínimo |
| `rdicon-thermostat-minimum-filled` | Termostato mínimo preenchido |
| `rdicon-thermostat-medium` | Termostato médio |
| `rdicon-thermostat-medium-filled` | Termostato médio preenchido |
| `rdicon-thermostat-maximum` | Termostato máximo |
| `rdicon-thermostat-maximum-filled` | Termostato máximo preenchido |
| `rdicon-snowflake` | Floco de neve (refrigerado) |
| `rdicon-stethoscope` | Estetoscópio |
| `rdicon-briefcase-medical` | Maleta médica |
| `rdicon-briefcase-medical-filled` | Maleta médica preenchido |
| `rdicon-health` | Saúde |
| `rdicon-health-filled` | Saúde preenchido |
| `rdicon-health-platform` | Plataforma saúde |
| `rdicon-health-plan` | Plano de saúde |
| `rdicon-heart-filled` | Coração preenchido |
| `rdicon-heart-outline` | Coração outline |
| `rdicon-heart-pulse` | Batimento cardíaco |
| `rdicon-heartbeat-machine` | Monitor cardíaco |
| `rdicon-heartbeat-machine-filled` | Monitor cardíaco preenchido |
| `rdicon-blood-donation` | Doação sangue |
| `rdicon-blood-donation-filled` | Doação sangue preenchido |
| `rdicon-blood-bag` | Bolsa de sangue |
| `rdicon-bone` | Osso |
| `rdicon-bone-broken` | Osso quebrado |
| `rdicon-x-ray-body` | Raio-X corpo |
| `rdicon-x-ray-body-filled` | Raio-X corpo preenchido |
| `rdicon-x-ray-bones` | Raio-X ossos |
| `rdicon-x-ray-bones-filled` | Raio-X ossos preenchido |
| `rdicon-virus` | Vírus |
| `rdicon-virus-filled` | Vírus preenchido |
| `rdicon-bacterium` | Bactéria |
| `rdicon-microscope` | Microscópio |
| `rdicon-test-tube` | Tubo de ensaio |
| `rdicon-test-tube-filled` | Tubo de ensaio preenchido |
| `rdicon-test-tube-variant` | Tubo de ensaio variante |
| `rdicon-lab` | Laboratório |
| `rdicon-pet-health` | Saúde pet |
| `rdicon-pet-health-filled` | Saúde pet preenchido |
| `rdicon-pet-medicine` | Medicamento pet |
| `rdicon-pet-medicine-filled` | Medicamento pet preenchido |

### Cuidados Pessoais

| Ícone | Descrição |
|-------|-----------|
| `rdicon-personal-care` | Cuidados pessoais |
| `rdicon-personal-care-filled` | Cuidados pessoais preenchido |
| `rdicon-cosmetics` | Cosméticos |
| `rdicon-dermocosmetic` | Dermocosméticos |
| `rdicon-perfumery` | Perfumaria |
| `rdicon-mask` | Máscara facial |
| `rdicon-mask-filled` | Máscara facial preenchido |
| `rdicon-soap` | Sabonete |
| `rdicon-scale-weight` | Balança |
| `rdicon-scale-weight-filled` | Balança preenchido |
| `rdicon-cream` | Creme |
| `rdicon-liquid-drop` | Gota líquida |
| `rdicon-drop` | Gota |
| `rdicon-generico` | Genérico |
| `rdicon-various` | Diversos |
| `rdicon-fruit-apple` | Maçã |
| `rdicon-fruit-apple-filled` | Maçã preenchido |
| `rdicon-yin-yang` | Yin Yang |
| `rdicon-smoking-off` | Não fumar |

### Bem-estar

| Ícone | Descrição |
|-------|-----------|
| `rdicon-treino` | Treino |
| `rdicon-habits` | Hábitos |
| `rdicon-balance` | Equilíbrio |
| `rdicon-sleep` | Sono |
| `rdicon-target` | Objetivo |

### Documentos

| Ícone | Descrição |
|-------|-----------|
| `rdicon-document` | Documento |
| `rdicon-document-filled` | Documento preenchido |
| `rdicon-document-variant` | Documento variante |
| `rdicon-document-variant-filled` | Documento variante preenchido |
| `rdicon-document-checkmark` | Documento confirmado |
| `rdicon-document-error` | Documento erro |
| `rdicon-document-warning` | Documento aviso |
| `rdicon-document-clock` | Documento relógio |
| `rdicon-document-edit` | Documento editar |
| `rdicon-document-help` | Documento ajuda |
| `rdicon-document-excel` | Documento Excel |
| `rdicon-notepad` | Bloco de notas |
| `rdicon-notepad-filled` | Bloco de notas preenchido |
| `rdicon-clipboard` | Prancheta |
| `rdicon-folder` | Pasta |
| `rdicon-folder-filled` | Pasta preenchido |
| `rdicon-folder-plus` | Adicionar pasta |
| `rdicon-folder-zip` | Pasta compactada |
| `rdicon-folder-zip-filled` | Pasta compactada preenchido |
| `rdicon-bookmark` | Marcador |
| `rdicon-list-bullet` | Lista |
| `rdicon-list-bullet-filled` | Lista preenchido |
| `rdicon-magazine` | Revista |
| `rdicon-magazine-filled` | Revista preenchido |
| `rdicon-magazine-sorria` | Revista Sorria |
| `rdicon-magazine-sorria-filled` | Revista Sorria preenchido |
| `rdicon-news` | Notícias |
| `rdicon-news-filled` | Notícias preenchido |

### Segurança

| Ícone | Descrição |
|-------|-----------|
| `rdicon-lock-closed` | Cadeado fechado |
| `rdicon-lock-closed-filled` | Cadeado fechado preenchido |
| `rdicon-lock-open` | Cadeado aberto |
| `rdicon-lock-open-filled` | Cadeado aberto preenchido |
| `rdicon-lock-open-variant` | Cadeado aberto variante |
| `rdicon-lock-open-variant-filled` | Cadeado aberto variante preenchido |
| `rdicon-password` | Senha |
| `rdicon-password-filled` | Senha preenchido |
| `rdicon-password-off` | Senha oculta |
| `rdicon-password-plus` | Adicionar senha |
| `rdicon-password-return` | Recuperar senha |
| `rdicon-password-refresh` | Atualizar senha |
| `rdicon-password-help` | Ajuda senha |

### Dispositivos

| Ícone | Descrição |
|-------|-----------|
| `rdicon-mobile` | Celular |
| `rdicon-mobile-credit` | Celular crédito |
| `rdicon-laptop` | Notebook |
| `rdicon-desktop` | Desktop |
| `rdicon-wifi` | WiFi |
| `rdicon-apple` | Apple |
| `rdicon-android` | Android |

### Iluminação

| Ícone | Descrição |
|-------|-----------|
| `rdicon-lightbulb-on` | Lâmpada acesa |
| `rdicon-lightbulb-on-filled` | Lâmpada acesa preenchido |
| `rdicon-lightbulb-off` | Lâmpada apagada |
| `rdicon-lightbulb-off-filled` | Lâmpada apagada preenchido |
| `rdicon-flashlight-on` | Lanterna acesa |
| `rdicon-flashlight-on-filled` | Lanterna acesa preenchido |
| `rdicon-flashlight-variant-on` | Lanterna variante acesa |
| `rdicon-flashlight-variant-on-filled` | Lanterna variante acesa preenchido |
| `rdicon-flashlight-off` | Lanterna apagada |

### Marketing

| Ícone | Descrição |
|-------|-----------|
| `rdicon-megaphone` | Megafone |
| `rdicon-megaphone-filled` | Megafone preenchido |
| `rdicon-megaphone-loud` | Megafone alto |
| `rdicon-megaphone-loud-filled` | Megafone alto preenchido |

### Gráficos e Dados

| Ícone | Descrição |
|-------|-----------|
| `rdicon-chart-area` | Gráfico área |
| `rdicon-chart-area-filled` | Gráfico área preenchido |
| `rdicon-chart-bar-horizontal` | Gráfico barras horizontal |
| `rdicon-chart-bar-vertical` | Gráfico barras vertical |
| `rdicon-chart-pie` | Gráfico pizza |
| `rdicon-chart-trending` | Gráfico tendência |
| `rdicon-chart-down` | Gráfico queda |
| `rdicon-dashboard` | Dashboard |
| `rdicon-speedometer` | Velocímetro |
| `rdicon-speedometer-filled` | Velocímetro preenchido |

### Redes Sociais

| Ícone | Descrição |
|-------|-----------|
| `rdicon-facebook` | Facebook |
| `rdicon-instagram` | Instagram |
| `rdicon-twitter` | Twitter |
| `rdicon-whatsapp` | WhatsApp |
| `rdicon-messenger` | Messenger |
| `rdicon-linkedin` | LinkedIn |
| `rdicon-social` | Social |
| `rdicon-social-filled` | Social preenchido |

### Marcas RD

| Ícone | Descrição |
|-------|-----------|
| `rdicon-drogasil` | Drogasil |
| `rdicon-droga-raia` | Droga Raia |
| `rdicon-raiadrogasil` | RaiaDrogasil |
| `rdicon-RD-saude` | RD Saúde |
| `rdicon-pulso` | Pulso |
| `rdicon-pulso-filled` | Pulso preenchido |
| `rdicon-stix` | Stix |
| `rdicon-livelo` | Livelo |

### Formulários

| Ícone | Descrição |
|-------|-----------|
| `rdicon-radio-button-unselected` | Radio não selecionado |
| `rdicon-radio-button-selected` | Radio selecionado |
| `rdicon-checkbox-unchecked` | Checkbox não marcado |
| `rdicon-checkbox-checked` | Checkbox marcado |
| `rdicon-checkbox-indeterminate` | Checkbox indeterminado |
| `rdicon-circle-plus` | Círculo com mais |
| `rdicon-circle-plus-filled` | Círculo com mais preenchido |

### Contadores

| Ícone | Descrição |
|-------|-----------|
| `rdicon-counter-1` até `rdicon-counter-9` | Contadores 1-9 |
| `rdicon-counter-9-plus` | Contador 9+ |
| `rdicon-counter-1-filled` até `rdicon-counter-9-filled` | Contadores preenchidos 1-9 |
| `rdicon-counter-9-plus-filled` | Contador 9+ preenchido |

### Outros

| Ícone | Descrição |
|-------|-----------|
| `rdicon-default` | Ícone padrão |
| `rdicon-home-outline` | Casa outline |
| `rdicon-home-filled` | Casa preenchido |
| `rdicon-production` | Produção |
| `rdicon-production-filled` | Produção preenchido |
| `rdicon-car-variant` | Carro |
| `rdicon-car-variant-filled` | Carro preenchido |
| `rdicon-cake` | Bolo |
| `rdicon-cake-filled` | Bolo preenchido |
| `rdicon-graduation-cap` | Chapéu formatura |
| `rdicon-graduation-cap-filled` | Chapéu formatura preenchido |
| `rdicon-digital-tip` | Dica digital |
| `rdicon-apps` | Aplicativos |
| `rdicon-apps-filled` | Aplicativos preenchido |

---

## Troubleshooting (Resolução de Problemas)

### Problema: Estilos não estão sendo aplicados

**Causa:** Falta da importação do CSS da biblioteca.

**Solução:**
```tsx
// Adicione no ponto de entrada da aplicação
import '@rdsaude/pulso-react-components/styles.css'
```

### Problema: Erro "Cannot find module '@rdsaude/pulso-react-components'"

**Causa:** Pacote não instalado ou versão do Node.js incompatível.

**Solução:**
```bash
# Verifique a versão do Node.js (deve ser >= 18)
node -v

# Reinstale as dependências
rm -rf node_modules package-lock.json
npm install
```

### Problema: Erro de TypeScript com componentes

**Causa:** Versão do TypeScript incompatível ou falta de tipos.

**Solução:**
```bash
# Atualize o TypeScript para versão 5.x
npm install typescript@latest --save-dev

# Verifique o tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "bundler", // ou "node16" / "nodenext"
    "esModuleInterop": true,
    "jsx": "react-jsx"
  }
}
```

### Problema: Conflito de versões do React

**Causa:** Múltiplas versões do React instaladas.

**Solução:**
```bash
# Verifique versões duplicadas
npm ls react

# Force uma única versão no package.json
{
  "resolutions": {
    "react": "18.3.1",
    "react-dom": "18.3.1"
  }
}

# Para npm (use overrides ao invés de resolutions)
{
  "overrides": {
    "react": "18.3.1",
    "react-dom": "18.3.1"
  }
}
```

### Problema: Componentes não renderizam corretamente no Next.js

**Causa:** Falta de configuração de transpilação.

**Solução:**
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@rdsaude/pulso-react-components'],
}

module.exports = nextConfig
```

### Problema: Ícones não aparecem

**Causa:** Falta da biblioteca de ícones ou CSS dos ícones.

**Solução:**
```bash
# Instale a biblioteca de ícones
npm install @raiadrogasil/pulso-icons
```

```tsx
// Importe o CSS dos ícones se necessário
import '@raiadrogasil/pulso-icons/pulsodesignsystem/style.css'
```

### Problema: ThemeProvider não aplica o tema

**Causa:** ThemeProvider não está envolvendo a aplicação corretamente.

**Solução:**
```tsx
// Certifique-se de que ThemeProvider é o componente mais externo
function App() {
  return (
    <ThemeProvider theme="rdsaudesistemas">
      {/* TODA a aplicação deve estar dentro */}
      <Router>
        <Layout>
          <Pages />
        </Layout>
      </Router>
    </ThemeProvider>
  )
}
```

### Problema: Erro "window is not defined" no SSR

**Causa:** Componentes tentando acessar APIs do browser no servidor.

**Solução:**
```tsx
// Use dynamic import com ssr: false no Next.js
import dynamic from 'next/dynamic'

const Modal = dynamic(
  () => import('@rdsaude/pulso-react-components').then(mod => mod.Modal),
  { ssr: false }
)
```

---

## Versões e Changelog

### Versões Recomendadas dos Pacotes

| Pacote | Versão Estável |
|--------|----------------|
| `@rdsaude/pulso-react-components` | `latest` |
| `@raiadrogasil/pulso-design-tokens` | `latest` |
| `@raiadrogasil/pulso-icons` | `latest` |

### Compatibilidade com Frameworks

| Framework | Versão Mínima | Status |
|-----------|---------------|--------|
| React | 18.0.0 | ✅ Suportado |
| Next.js | 13.0.0 | ✅ Suportado |
| Vite | 4.0.0 | ✅ Suportado |
| Create React App | 5.0.0 | ✅ Suportado |
| Remix | 1.0.0 | ⚠️ Compatível (não testado oficialmente) |
| Gatsby | 5.0.0 | ⚠️ Compatível (não testado oficialmente) |

---

Este documento deve ser usado como referência para implementar interfaces usando o Pulso Design System. Sempre siga as estruturas de composição e props documentadas para garantir a consistência e funcionalidade correta dos componentes.

**Links Úteis:**
- 📦 [NPM - @rdsaude/pulso-react-components](https://www.npmjs.com/package/@rdsaude/pulso-react-components)
- 📦 [NPM - @raiadrogasil/pulso-design-tokens](https://www.npmjs.com/package/@raiadrogasil/pulso-design-tokens)
- 📦 [NPM - @raiadrogasil/pulso-icons](https://www.npmjs.com/package/@raiadrogasil/pulso-icons)
- 🎨 [Storybook - Documentação Visual](https://pulso.rd.com.br/)