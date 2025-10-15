FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Clean install with verbose output
RUN npm ci --verbose

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
