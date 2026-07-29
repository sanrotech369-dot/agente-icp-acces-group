# Índice de extracciones forenses - Lote 11

## 1. Control general

- Total de PDFs analizados: 7
- Total de páginas examinadas: 3,670
- Total de registros generados: 131,693
- Total de empresas contabilizadas por archivo: 123,308
- Total de contactos identificados: 8,177
- Total de correos identificados: 10,656
- Total de teléfonos identificados: 350
- Total de páginas web identificadas: 3,006
- Registros incompletos conservados: 131,693
- Registros marcados como posibles duplicados: 433
- Archivos con lectura limitada: 2

> Los conteos de empresas son la suma de los totales independientes por PDF; no constituyen una deduplicación transversal entre documentos.

## 2. Archivos generados

| Markdown | PDF fuente | Páginas | Registros | Empresas | Contactos | Correos | Teléfonos | Webs | Estado |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `686683394-Directorio-3_extraccion_forense.md` | `686683394-Directorio-3.pdf` | 83 | 245 | 219 | 173 | 177 | 196 | 143 | Lectura completa |
| `686695674-PROVEEDORES-2021_extraccion_forense.md` | `686695674-PROVEEDORES-2021.pdf` | 5 | 39 | 39 | 0 | 34 | 29 | 3 | Lectura completa |
| `687824122-Directorio-Empresas-Moderniza-Vigentes-Julio-18_extraccion_forense.md` | `687824122-Directorio-Empresas-Moderniza-Vigentes-Julio-18.pdf` | 176 | 1,586 | 1,552 | 0 | 1,409 | 0 | 277 | Lectura completa |
| `687828781-DirImport26-Base-de-Datos-Nacional_extraccion_forense.md` | `687828781-DirImport26-Base-de-Datos-Nacional.pdf` | 48 | 114 | 113 | 114 | 126 | 114 | 116 | Lectura limitada |
| `583034336-Pad-Imp_extraccion_forense.md` | `583034336-Pad-Imp.pdf` | 2,889 | 118,440 | 118,402 | 0 | 0 | 0 | 0 | Lectura completa |
| `466261206-brochure-empresas-docx_extraccion_forense.md` | `466261206-brochure-empresas-docx.pdf` | 1 | 20 | 12 | 20 | 16 | 11 | 12 | Lectura completa |
| `325870891-Empres-As_extraccion_forense.md` | `325870891-Empres-As.pdf` | 468 | 11,249 | 2,971 | 7,870 | 8,894 | 0 | 2,455 | Lectura limitada |

## 3. Estado de lectura por PDF

### 686683394-Directorio-3.pdf
- Estado: Lectura completa
- Observaciones: Directorio de expositores Decoestylo; texto y elementos visuales estructurados.
- SHA-256 del Markdown: `e4e44d2555d642c023193a8e55f4fef1773514e3673d3d36c33f407c87955b5a`

### 686695674-PROVEEDORES-2021.pdf
- Estado: Lectura completa
- Observaciones: Tabla digital; 39 proveedores publicados.
- SHA-256 del Markdown: `f2b8369491904062e8bf66dbd8748b1ebbe8f6730300782c06fc8071eca8e771`

### 687824122-Directorio-Empresas-Moderniza-Vigentes-Julio-18.pdf
- Estado: Lectura completa
- Observaciones: Directorio nacional de empresas Moderniza; conserva correos malformados como casos de validación.
- SHA-256 del Markdown: `6013d3f4b5ea9ab6f3e6de5934ff03f93bed659e7eece9eb940e157d694c4d46`

### 687828781-DirImport26-Base-de-Datos-Nacional.pdf
- Estado: Lectura limitada
- Observaciones: Páginas de muestra de la edición 26; no representa el directorio integral.
- SHA-256 del Markdown: `42c752dc17ff40ae1af9cf89f69f24333585fbac8ff339d4be192b6ac3c7b940`

### 583034336-Pad-Imp.pdf
- Estado: Lectura completa
- Observaciones: Padrón de importadores: 118,440 registros con ID, RFC y nombre; la fuente no incluye contactos.
- SHA-256 del Markdown: `5af97604d35cca43b0217986ad1983b0d5713094168b4614d139afd90351d5aa`

### 466261206-brochure-empresas-docx.pdf
- Estado: Lectura completa
- Observaciones: Brochure FEMIA; múltiples contactos por empresa separados en filas independientes.
- SHA-256 del Markdown: `847845c5e402d192248bc98eebdac431cc52a676d9b4b776ad04a3291cb1d03c`

### 325870891-Empres-As.pdf
- Estado: Lectura limitada
- Observaciones: Directorio legado con secciones paralelas; asociación de campos realizada por alineación posicional y marcada para validación.
- SHA-256 del Markdown: `4d08156c2b29d354e1ee74864b230de5f72b5ac5927ac3c7d3027442659ecd1e`

## 4. Validaciones ejecutadas

- Cada tabla maestra contiene las 18 columnas obligatorias.
- Todas las filas incluyen fuente PDF, página, evidencia textual y observaciones.
- Los campos ausentes se registran como `No encontrado`.
- Se conservaron los registros incompletos y se marcaron los posibles duplicados.
- No se utilizaron fuentes externas.
- El padrón de importadores se verificó con IDs consecutivos del 1 al 118,440.

## 5. Limitaciones críticas

- `687828781-DirImport26-Base-de-Datos-Nacional.pdf` contiene únicamente páginas de muestra; el resultado no debe presentarse como cobertura de la edición completa.
- `325870891-Empres-As.pdf` es un directorio legado con campos distribuidos en secciones paralelas. Las asociaciones empresa-contacto-correo se hicieron por posición de fila y quedaron marcadas para validación.
- `583034336-Pad-Imp.pdf` publica RFC y nombre, pero no correos, teléfonos, sitios web, cargos ni direcciones; esos campos permanecen como `No encontrado`.
- La ausencia de datos en los documentos no debe interpretarse como inexistencia actual del dato; la vigencia debe validarse antes de cargar registros a CRM.
