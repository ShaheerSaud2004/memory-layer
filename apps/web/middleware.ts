import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

/**
 * Console auth is API JWT in localStorage; Clerk is optional for /sign-in.
 * Keep these routes public so marketing + JWT login are not redirected to Clerk.
 */
const isPublicRoute = createRouteMatcher([
  "/",
  "/login(.*)",
  "/status(.*)",
  "/dashboard(.*)",
  "/billing(.*)",
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/health-proxy(.*)",
]);

export default clerkMiddleware(async (auth, req) => {
  if (!isPublicRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
