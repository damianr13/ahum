"use client";

import MainComponent from "@/components/main";
import React from "react";
import Head from "next/head";

export default function Home() {
  return (
    <div>
      <Head>
        <meta name="robots" content="noindex" />
      </Head>
      <MainComponent />
    </div>
  );
}
