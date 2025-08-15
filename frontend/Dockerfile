# ---- Build Stage ----
# Use a Node.js image to build the app
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# ---- Serve Stage ----
# Use a lightweight Nginx image to serve the static files
FROM nginx:1.25-alpine

# Copy the build output from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# Nginx will automatically serve the index.html file
EXPOSE 80