/* Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement. */

import { Icon } from "@iconify/react";

function Footer() {
  return (
    <>
      <footer className="w-full bg-card border-t border-border text-foreground transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-6 py-12 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
            {/* Brand Info Section */}
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center gap-2">
                <Icon
                  icon="fa-solid:chart-line"
                  className="h-7 w-7 text-accent"
                />
                <span className="font-bold text-2xl tracking-tight text-accent">
                  BrandPulse
                </span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed max-w-sm">
                Real-time AI social media monitoring and sentiment analysis
                platform designed to track brand health, customer intent, and
                market trends seamlessly.
              </p>
              
            </div>

            {/* Platform Links */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">
                Product
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <a
                    href="#dashboard"
                    className="hover:text-accent transition-colors"
                  >
                    Real-time Dashboard
                  </a>
                </li>
                <li>
                  <a
                    href="#feed"
                    className="hover:text-accent transition-colors"
                  >
                    Live Sentiment Feed
                  </a>
                </li>
                <li>
                  <a
                    href="#sources"
                    className="hover:text-accent transition-colors"
                  >
                    Source Management
                  </a>
                </li>
                <li>
                  <a
                    href="#analytics"
                    className="hover:text-accent transition-colors"
                  >
                    Intent Analytics
                  </a>
                </li>
              </ul>
            </div>

            {/* Development Team */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">
                Development Team
              </h3>
              <ul className="space-y-2.5 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <Icon
                    icon="lucide:code-2"
                    className="w-4 h-4 text-accent"
                  />
                  <span>Muhammad Basim Irfan</span>
                </li>
                <li className="flex items-center gap-2">
                  <Icon
                    icon="lucide:code-2"
                    className="w-4 h-4 text-accent"
                  />
                  <span>Momina Shahid</span>
                </li>
                <li className="flex items-center gap-2">
                  <Icon
                    icon="lucide:code-2"
                    className="w-4 h-4 text-accent"
                  />
                  <span>Muhammad Ismail Rana</span>
                </li>
              </ul>
            </div>

            {/* Status & Technology */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-foreground">
                System
              </h3>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-(--positive-bg) text-(--positive-text) text-xs font-medium">
                <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
                <span>Monitoring Engines Active</span>
              </div>
              <p className="text-xs text-muted-foreground pt-2 leading-relaxed">
                Powered by custom AI sentiment pipelines and modern web
                architecture.
              </p>
            </div>
          </div>

          {/* Bottom Bar / Copyright */}
          <div className="mt-12 pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
            <p>© {new Date().getFullYear()} BrandPulse. All rights reserved.</p>
            <div className="flex items-center gap-6">
              <a
                href="#privacy"
                className="hover:text-accent transition-colors"
              >
                Privacy Policy
              </a>
              <a
                href="#terms"
                className="hover:text-accent transition-colors"
              >
                Terms of Service
              </a>
              <a
                href="#documentation"
                className="hover:text-accent transition-colors"
              >
                API Docs
              </a>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}

export default Footer;
