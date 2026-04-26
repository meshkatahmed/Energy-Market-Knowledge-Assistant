# --- Build Stage ---
FROM node:20-alpine as build-stage

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application
# We use an argument to pass the API URL at build time if needed,
# or it can be handled at runtime with a script (common in Docker/Nginx setups).
# For Vite, we'll use build-time env vars.
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# --- Production Stage ---
FROM nginx:stable-alpine as production-stage

# Copy the build output to nginx's serve directory
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy a custom nginx configuration if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
