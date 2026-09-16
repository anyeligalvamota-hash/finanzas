# Finanza · Tu vida en equilibrio

Proyecto listo para importar como un proyecto nuevo en Vercel o subir a un repositorio GitHub.

## Despliegue en Vercel
1. Importa este repositorio/proyecto en Vercel.
2. No necesita comando de build: `index.html` es la entrada web.
3. Conecta el mismo Vercel Blob Store privado que contiene los datos actuales.
4. Verifica la variable `BLOB_READ_WRITE_TOKEN` (o la configuración OIDC del Blob Store).

### Importante sobre los datos
Este paquete NO incluye `Anyeli.json` ni datos financieros personales. La aplicación sincroniza los datos por usuario mediante Vercel Blob. Para conservar los datos existentes al crear el proyecto nuevo, el nuevo proyecto debe tener acceso al mismo Blob Store privado y a sus credenciales.

## GitHub
Puedes subir el contenido de este paquete a un repositorio nuevo, por ejemplo `finanzas-en-equilibrio`. Los workflows de `.github/workflows/` están incluidos.

## Incluye
- Dashboard y presupuesto vs gastos.
- Total mensual de presupuesto y porcentaje ejecutado.
- Cuotas y mensualidades dentro del presupuesto.
- Eliminación de categorías sin borrar movimientos históricos.
- Gráfico de deudas por porcentaje del total.
- Temas y personalización de diseño.
- Sincronización remota por usuario.
- API Vercel para almacenamiento privado.
