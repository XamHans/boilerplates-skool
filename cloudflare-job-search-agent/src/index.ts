import { getAgentByName, routeAgentRequest } from "agents";
import { JobSearchAgent } from "./agents/job-search";

export { JobSearchAgent };

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const agentResponse = await routeAgentRequest(request, env);
    if (agentResponse) return agentResponse;

    const url = new URL(request.url);

    if (url.pathname === "/") {
      return Response.json({
        name: "cloudflare-job-search-agent",
        routes: {
          run: "POST /job-search/:name/run",
          note: "Use a stable :name (e.g. 'main') per real-world instance. Any new name starts a fresh Durable Object."
        }
      });
    }

    const jobSearchMatch = url.pathname.match(/^\/job-search\/([^/]+)\/run$/);
    if (jobSearchMatch && request.method === "POST") {
      const agent = await getAgentByName<Env, JobSearchAgent>(
        env.JobSearchAgent as DurableObjectNamespace<JobSearchAgent>,
        jobSearchMatch[1]
      );
      return Response.json(await agent.runWeeklyScan());
    }

    return new Response("Not found", { status: 404 });
  },

  async scheduled(_controller: ScheduledController, env: Env): Promise<void> {
    const agent = await getAgentByName<Env, JobSearchAgent>(
      env.JobSearchAgent as DurableObjectNamespace<JobSearchAgent>,
      "main"
    );
    await agent.runWeeklyScan();
  }
};
