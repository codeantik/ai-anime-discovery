export async function GET() {
  return Response.json({ BACKEND_URL: process.env.BACKEND_URL ?? "UNSET" });
}
