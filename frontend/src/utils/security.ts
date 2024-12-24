export const generateSecureToken = (tableNumber: number) => {
  const timestamp = Date.now();
  const randomString = Math.random().toString(36).substring(2, 8);
  return `${tableNumber}-${timestamp}-${randomString}`;
}; 