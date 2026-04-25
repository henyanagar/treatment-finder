FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

# EX2 prefers running Vite in dev mode for instructor demonstration.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
