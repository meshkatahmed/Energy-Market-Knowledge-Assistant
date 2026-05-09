# We use an argument to pass the API URL at build time if needed,
# or it can be handled at runtime with a script (common in Docker/Nginx setups).
# For Vite, we'll use build-time env vars.
# ARG VITE_API_URL
# ENV VITE_API_URL=$VITE_API_URL

# RUN npm run build

# Copy the build output to nginx's serve directory
# COPY --from=build /app/dist /usr/share/nginx/html

# Install web server
# RUN apk update && apk add nginx

# Make nginx's serve directory and copy the build output to that
# RUN mkdir -p /usr/share/nginx/html && cp -r /app/dist/* /usr/share/nginx/html/

# Copy a custom nginx configuration if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf





# --- Build Stage ---
FROM node:20-alpine AS BUILD

# Set up working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Set environment variable for API URL (can be overridden at runtime)
# ARG VITE_BACKEND_URL
# ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build


# Production stage
FROM nginx:stable-alpine

# Copy the build output to nginx's serve directory
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
