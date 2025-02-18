const express = require("express");
const router = express.Router();
const axios = require("axios");

const GITHUB_API_URL = "https://api.github.com";

router.get("/stats/:username", async (req, res) => {
  try {
    const { username } = req.params;
    const headers = {
      Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github.v3+json",
    };

    // Fetch user profile
    const userResponse = await axios.get(
      `${GITHUB_API_URL}/users/${username}`,
      { headers }
    );

    // Fetch repositories
    const reposResponse = await axios.get(
      `${GITHUB_API_URL}/users/${username}/repos`,
      { headers }
    );

    // Fetch contributions (requires GraphQL API)
    const contributionsQuery = `
      query {
        user(login: "${username}") {
          contributionsCollection {
            totalCommitContributions
            restrictedContributionsCount
            totalPullRequestContributions
            totalIssueContributions
          }
          repositories(first: 100, orderBy: {field: STARGAZERS, direction: DESC}) {
            totalCount
            nodes {
              stargazerCount
              languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                edges {
                  size
                  node {
                    name
                    color
                  }
                }
              }
            }
          }
        }
      }
    `;

    const graphqlResponse = await axios.post(
      "https://api.github.com/graphql",
      { query: contributionsQuery },
      { headers }
    );

    // Process and combine the data
    const userData = userResponse.data;
    const repos = reposResponse.data;
    const contributionsData = graphqlResponse.data.data.user;

    // Calculate total stars
    const totalStars = repos.reduce(
      (sum, repo) => sum + repo.stargazers_count,
      0
    );

    // Calculate language statistics
    const languages = {};
    repos.forEach((repo) => {
      if (repo.language) {
        languages[repo.language] = (languages[repo.language] || 0) + 1;
      }
    });

    const response = {
      profile: {
        name: userData.name,
        avatar_url: userData.avatar_url,
        bio: userData.bio,
        followers: userData.followers,
        following: userData.following,
        public_repos: userData.public_repos,
      },
      stats: {
        stars: totalStars,
        repositories: repos.length,
        languages: Object.entries(languages).map(([name, count]) => ({
          name,
          count,
          percentage: ((count / repos.length) * 100).toFixed(1),
        })),
      },
      contributions: {
        total:
          contributionsData.contributionsCollection.totalCommitContributions,
        pulls:
          contributionsData.contributionsCollection
            .totalPullRequestContributions,
        issues:
          contributionsData.contributionsCollection.totalIssueContributions,
      },
    };

    res.json(response);
  } catch (error) {
    console.error("GitHub API Error:", error.response?.data || error.message);
    res.status(500).json({
      error: "Failed to fetch GitHub stats",
      details: error.response?.data || error.message,
    });
  }
});

module.exports = router;
